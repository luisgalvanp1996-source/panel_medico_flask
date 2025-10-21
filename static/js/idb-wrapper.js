// idb-wrapper.js - minimal promise-based IndexedDB helper
const IDB_DB_NAME = 'panel_medico_db';
const IDB_DB_VERSION = 2;
let dbPromise = null;

function openDb() {
  if (dbPromise) return dbPromise;
  dbPromise = new Promise((resolve, reject) => {
    const req = indexedDB.open(IDB_DB_NAME, IDB_DB_VERSION);
    req.onupgradeneeded = (e) => {
      const db = e.target.result;
      if (!db.objectStoreNames.contains('pacientes')) {
        db.createObjectStore('pacientes', { keyPath: 'id' });
      }
      if (!db.objectStoreNames.contains('medicos')) {
        db.createObjectStore('medicos', { keyPath: 'id' });
      }
      if (!db.objectStoreNames.contains('pendientes')) {
        db.createObjectStore('pendientes', { autoIncrement: true });
      }
      if (!db.objectStoreNames.contains('rondas')) {
        db.createObjectStore('rondas', { keyPath: 'local_id' });
      }
      if (!db.objectStoreNames.contains('id_map')) {
        db.createObjectStore('id_map', { keyPath: 'local_id' });
      }
    };
    req.onsuccess = () => resolve(req.result);
    req.onerror = () => reject(req.error);
  });
  return dbPromise;
}

async function putMany(storeName, items) {
  const db = await openDb();
  return new Promise((res, rej) => {
    const tx = db.transaction(storeName, 'readwrite');
    const store = tx.objectStore(storeName);
    items.forEach(it => store.put(it));
    tx.oncomplete = () => res();
    tx.onerror = () => rej(tx.error);
  });
}

async function getAll(storeName) {
  const db = await openDb();
  return new Promise((res, rej) => {
    const tx = db.transaction(storeName, 'readonly');
    const store = tx.objectStore(storeName);
    const req = store.getAll();
    req.onsuccess = () => res(req.result);
    req.onerror = () => rej(req.error);
  });
}

async function addPendiente(item) {
  const db = await openDb();
  return new Promise((res, rej) => {
    const tx = db.transaction('pendientes', 'readwrite');
    tx.objectStore('pendientes').add(item);
    tx.oncomplete = () => res();
    tx.onerror = () => rej(tx.error);
  });
}

async function getPendientes() {
  const db = await openDb();
  return new Promise((res, rej) => {
    const tx = db.transaction('pendientes', 'readonly');
    const req = tx.objectStore('pendientes').getAll();
    req.onsuccess = () => res(req.result);
    req.onerror = () => rej(tx.error);
  });
}

async function clearPendientes() {
  const db = await openDb();
  return new Promise((res, rej) => {
    const tx = db.transaction('pendientes', 'readwrite');
    tx.objectStore('pendientes').clear();
    tx.oncomplete = () => res();
    tx.onerror = () => rej(tx.error);
  });
}
