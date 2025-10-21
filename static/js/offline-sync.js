// offline-sync.js
async function fetchAndStore(path, storeName) {
  try {
    const resp = await fetch(path);
    if (!resp.ok) throw new Error('Network response not ok');
    const data = await resp.json();
    await putMany(storeName, data);
    console.log('Stored', data.length, 'into', storeName);
    return data;
  } catch (err) {
    console.warn('Fetch failed for', path, err);
    const local = await getAll(storeName);
    return local;
  }
}

async function initialLoad() {
  if (navigator.onLine) {
    await fetchAndStore('/api/pacientes', 'pacientes');
    await fetchAndStore('/api/medicos', 'medicos');
  } else {
    console.log('Offline: using local stores');
  }
  if (navigator.onLine) {
    await syncPendientes();
  }
}

async function syncPendientes() {
  const pendientes = await getPendientes();
  if (!pendientes || pendientes.length === 0) return;
  // shape pendientes for server: ensure they contain table and data and local_id
  const payload = { pendientes: pendientes.map(p => {
    // if rondas created locally may have local_id field
    return p;
  }) };
  try {
    const resp = await fetch('/sync/push', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    if (resp.ok) {
      const data = await resp.json();
      // update id_map in IDB if mappings returned
      if (data.mappings && data.mappings.length) {
        await putMany('id_map', data.mappings.map(m => ({ local_id: m.local_id, sqlite_rowid: m.sqlite_rowid, table: m.table })));
      }
      await clearPendientes();
      console.log('Pendientes sent and cleared');
      // trigger server-side push to SQL Server
      await fetch('/sync/pull', { method: 'POST' });
    } else {
      console.warn('Failed to send pendientes', await resp.text());
    }
  } catch (err) {
    console.warn('Error sending pendientes', err);
  }
}

// helper to add a new ronda from UI offline
async function createRondaOffline(ronda) {
  // ensure local_id exists
  if (!ronda.local_id) {
    ronda.local_id = crypto.randomUUID();
  }
  // store in 'rondas' store and also add to pendientes
  await putMany('rondas', [ronda]);
  await addPendiente({ table: 'Rondas', data: ronda, local_id: ronda.local_id });
  if (navigator.onLine) {
    await syncPendientes();
  }
}

// expose
window.initialLoad = initialLoad;
window.createRondaOffline = createRondaOffline;
