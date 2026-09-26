const loginScreen = document.querySelector("#login-screen");
const appScreen = document.querySelector("#app-screen");
const loginForm = document.querySelector("#login-form");
const loginStatus = document.querySelector("#login-status");
const sessionUsername = document.querySelector("#session-username");
const sessionRole = document.querySelector("#session-role");
const logoutButton = document.querySelector("#logout-button");
const sidebarToggle = document.querySelector("#sidebar-toggle");
const adminNavButtons = () => document.querySelectorAll(".admin-nav");
const navButtons = () => document.querySelectorAll("[data-view]");
const viewTitle = document.querySelector("#view-title");
const searchView = document.querySelector("#search-view");
const archiveView = document.querySelector("#archive-view");
const createView = document.querySelector("#create-view");
const adminView = document.querySelector("#admin-view");
const projectsList = document.querySelector("#projects-list");
const projectCount = document.querySelector("#project-count");
const archiveFilterInput = document.querySelector("#archive-filter");
const archiveFilterClear = document.querySelector("#archive-filter-clear");
const projectDetail = document.querySelector("#project-detail");
const searchForm = document.querySelector("#search-form");
const searchQuery = document.querySelector("#search-query");
const resultsPanel = document.querySelector("#results-panel");
const results = document.querySelector("#results");
const resultsSummary = document.querySelector("#results-summary");
const userForm = document.querySelector("#user-form");
const userFormStatus = document.querySelector("#user-form-status");
const usersList = document.querySelector("#users-list");
const PAGE_SIZE = 20;

const translations = {
  it: {
    "login.subtitle": "Archivio intelligente locale",
    "login.eyebrow": "Accesso",
    "login.title": "Entra nel workspace",
    "login.submit": "Accedi",
    "login.adminHint": "carica, cerca, gestisce utenti",
    "login.userHint": "solo ricerca",
    "brand.subtitle": "Il tuo archivio intelligente",
    "brand.mobileSubtitle": "Archivio locale",
    "nav.search": "Ricerca",
    "nav.archive": "Archivio progetti",
    "nav.create": "Crea progetto",
    "nav.accounts": "Account",
    "session.logout": "Esci",
    "sidebar.open": "Apri barra laterale",
    "sidebar.close": "Chiudi barra laterale",
    "role.admin": "Admin",
    "role.user": "Utente",
    "views.search": "Ricerca progetti",
    "views.archive": "Archivio progetti",
    "views.create": "Crea progetto",
    "views.admin": "Gestione account",
    "search.placeholder": "Cerca per caratteristiche...",
    "search.submit": "Cerca",
    "results.eyebrow": "Risultati",
    "results.ready": "Pronto per cercare",
    "results.searching": "Ricerca in corso",
    "results.searchingBody": "Confronto la query con i progetti indicizzati.",
    "results.error": "Errore",
    "results.none": "Nessun risultato",
    "results.noneBody": (query) => `Nessun progetto trovato per "${query}".`,
    "results.count": (count) => `${count} ${count === 1 ? "risultato" : "risultati"}`,
    "projects.eyebrow": "Progetti",
    "projects.uploadTitle": "Carica progetto",
    "projects.name": "Nome",
    "projects.namePlaceholder": "Es. Showroom Milano",
    "projects.files": "File",
    "projects.notes": "Note",
    "projects.notesPlaceholder": "Cliente, contesto, materiali",
    "projects.uploadSubmit": "Carica",
    "projects.archive": "Archivio",
    "projects.count": (count) => `${count} ${count === 1 ? "elemento" : "elementi"}`,
    "projects.empty": "Nessun progetto caricato.",
    "projects.noMatches": (query) => `Nessun progetto corrisponde a "${query}".`,
    "projects.filteredCount": (shown, total) => `${shown} di ${total}`,
    "pagination.previous": "Precedente",
    "pagination.next": "Successiva",
    "pagination.summary": (start, end, total) => `${start}-${end} di ${total}`,
    "pagination.page": (page, pages) => `Pagina ${page} di ${pages}`,
    "archive.filterPlaceholder": "Cerca per nome progetto...",
    "archive.filterClear": "Cancella ricerca",
    "projects.filesCount": (count) => `${count} file`,
    "projects.chunksCount": (count) => `${count} blocchi testo`,
    "projects.visualsCount": (count) => `${count} visual`,
    "projects.uploading": "Caricamento in corso...",
    "projects.uploaded": "Progetto ricevuto. Indicizzazione avviata.",
    "projectDetail.eyebrow": "Dettaglio progetto",
    "projectDetail.assets": "Asset",
    "projectDetail.noAssets": "Nessun asset disponibile.",
    "projectDetail.open": "Apri progetto",
    "projectDetail.preview": "Anteprima",
    "projectDetail.download": "Scarica",
    "projectDetail.metadata": "Dati progetto",
    "projectDetail.save": "Salva dati",
    "projectDetail.saving": "Salvo...",
    "projectDetail.saved": "Dati aggiornati.",
    "projectDetail.addAssetsTitle": "Aggiungi asset",
    "projectDetail.addAssetsHint": "Aggiunge nuovi file al progetto senza toccare quelli esistenti.",
    "projectDetail.selectFiles": "File da aggiungere",
    "projectDetail.addAssets": "Aggiungi",
    "projectDetail.addingAssets": "Aggiunta asset in corso...",
    "projectDetail.assetsAdded": "Asset aggiunti. Indicizzazione avviata.",
    "projectDetail.dangerZone": "Zona pericolosa",
    "projectDetail.delete": "Elimina progetto",
    "projectDetail.deleting": "Eliminazione...",
    "projectDetail.deleteHint": "Rimuove il progetto, gli asset e l'indice. Operazione irreversibile.",
    "projectDetail.confirmDelete": (title) => `Eliminare definitivamente il progetto "${title}"? L'operazione e' irreversibile.`,
    "projectDetail.assetStats": (chunks, visuals) => `${chunks} testo / ${visuals} visual`,
    "projectDetail.pages": (count) => `${count} pagine`,
    "accounts.eyebrow": "Account",
    "accounts.createTitle": "Crea utente",
    "accounts.username": "username",
    "accounts.password": "password",
    "accounts.createSubmit": "Crea",
    "accounts.access": "Accessi",
    "accounts.management": "Gestione utenti",
    "accounts.creating": "Creazione utente...",
    "accounts.created": "Utente creato.",
    "accounts.updated": "Accessi aggiornati.",
    "accounts.active": "attivo",
    "accounts.disabled": "disabilitato",
    "accounts.newPassword": "nuova password opzionale",
    "accounts.save": "Salva",
    "accounts.saving": "Salvo...",
    "accounts.delete": "Elimina",
    "accounts.deleting": "Elimino...",
    "accounts.deleted": "Utente eliminato.",
    "accounts.confirmDelete": (username) => `Eliminare definitivamente l'utente "${username}"?`,
    "accounts.cannotDeleteSelf": "Non puoi eliminare il tuo account",
    "accounts.youTag": "Tu",
    "accounts.roleLabel": "Ruolo",
    "accounts.statusLabel": "Stato",
    "accounts.languageLabel": "Lingua",
    "accounts.passwordLabel": "Nuova password",
    "auth.signingIn": "Accesso in corso...",
    "generic.operationFailed": "Operazione non riuscita",
    "generic.close": "Chiudi",
    "confirm.accept": "Conferma",
    "confirm.cancel": "Annulla",
    "confirm.deleteAccept": "Elimina",
    "evidence.visual": "visuale",
    "evidence.text": "testo",
    "evidence.visualPreview": "Anteprima visuale",
    "evidence.page": (page) => ` - pagina ${page}`,
    "evidence.preview": "Anteprima",
    "evidence.openFile": "Apri file",
    "status.queued": "in coda",
    "status.processing": "elabora",
    "status.ready": "pronto",
    "status.error": "errore",
  },
  en: {
    "login.subtitle": "Local intelligent archive",
    "login.eyebrow": "Sign in",
    "login.title": "Enter your workspace",
    "login.submit": "Sign in",
    "login.adminHint": "upload, search, manage users",
    "login.userHint": "search only",
    "brand.subtitle": "Your Intelligent Archive",
    "brand.mobileSubtitle": "Local archive",
    "nav.search": "Search",
    "nav.archive": "Project Archive",
    "nav.create": "Create Project",
    "nav.accounts": "Accounts",
    "session.logout": "Log out",
    "sidebar.open": "Open sidebar",
    "sidebar.close": "Close sidebar",
    "role.admin": "Admin",
    "role.user": "User",
    "views.search": "Project search",
    "views.archive": "Project Archive",
    "views.create": "Create Project",
    "views.admin": "Account management",
    "search.placeholder": "Search by features...",
    "search.submit": "Search",
    "results.eyebrow": "Results",
    "results.ready": "Ready to search",
    "results.searching": "Searching",
    "results.searchingBody": "Comparing the query with indexed projects.",
    "results.error": "Error",
    "results.none": "No results",
    "results.noneBody": (query) => `No project found for "${query}".`,
    "results.count": (count) => `${count} ${count === 1 ? "result" : "results"}`,
    "projects.eyebrow": "Projects",
    "projects.uploadTitle": "Upload project",
    "projects.name": "Name",
    "projects.namePlaceholder": "E.g. Milan Showroom",
    "projects.files": "Files",
    "projects.notes": "Notes",
    "projects.notesPlaceholder": "Client, context, materials",
    "projects.uploadSubmit": "Upload",
    "projects.archive": "Archive",
    "projects.count": (count) => `${count} ${count === 1 ? "item" : "items"}`,
    "projects.empty": "No projects uploaded yet.",
    "projects.noMatches": (query) => `No project matches "${query}".`,
    "projects.filteredCount": (shown, total) => `${shown} of ${total}`,
    "pagination.previous": "Previous",
    "pagination.next": "Next",
    "pagination.summary": (start, end, total) => `${start}-${end} of ${total}`,
    "pagination.page": (page, pages) => `Page ${page} of ${pages}`,
    "archive.filterPlaceholder": "Search by project name...",
    "archive.filterClear": "Clear search",
    "projects.filesCount": (count) => `${count} files`,
    "projects.chunksCount": (count) => `${count} text chunks`,
    "projects.visualsCount": (count) => `${count} visuals`,
    "projects.uploading": "Uploading...",
    "projects.uploaded": "Project received. Indexing has started.",
    "projectDetail.eyebrow": "Project detail",
    "projectDetail.assets": "Assets",
    "projectDetail.noAssets": "No assets available.",
    "projectDetail.open": "Open project",
    "projectDetail.preview": "Preview",
    "projectDetail.download": "Download",
    "projectDetail.metadata": "Project data",
    "projectDetail.save": "Save data",
    "projectDetail.saving": "Saving...",
    "projectDetail.saved": "Data updated.",
    "projectDetail.addAssetsTitle": "Add assets",
    "projectDetail.addAssetsHint": "Adds new files to the project without touching existing ones.",
    "projectDetail.selectFiles": "Files to add",
    "projectDetail.addAssets": "Add",
    "projectDetail.addingAssets": "Adding assets...",
    "projectDetail.assetsAdded": "Assets added. Indexing has started.",
    "projectDetail.dangerZone": "Danger zone",
    "projectDetail.delete": "Delete project",
    "projectDetail.deleting": "Deleting...",
    "projectDetail.deleteHint": "Removes the project, its assets and its index. This cannot be undone.",
    "projectDetail.confirmDelete": (title) => `Permanently delete project "${title}"? This cannot be undone.`,
    "projectDetail.assetStats": (chunks, visuals) => `${chunks} text / ${visuals} visuals`,
    "projectDetail.pages": (count) => `${count} pages`,
    "accounts.eyebrow": "Accounts",
    "accounts.createTitle": "Create user",
    "accounts.username": "username",
    "accounts.password": "password",
    "accounts.createSubmit": "Create",
    "accounts.access": "Access",
    "accounts.management": "User management",
    "accounts.creating": "Creating user...",
    "accounts.created": "User created.",
    "accounts.updated": "Access updated.",
    "accounts.active": "active",
    "accounts.disabled": "disabled",
    "accounts.newPassword": "new password optional",
    "accounts.save": "Save",
    "accounts.saving": "Saving...",
    "accounts.delete": "Delete",
    "accounts.deleting": "Deleting...",
    "accounts.deleted": "User deleted.",
    "accounts.confirmDelete": (username) => `Permanently delete user "${username}"?`,
    "accounts.cannotDeleteSelf": "You cannot delete your own account",
    "accounts.youTag": "You",
    "accounts.roleLabel": "Role",
    "accounts.statusLabel": "Status",
    "accounts.languageLabel": "Language",
    "accounts.passwordLabel": "New password",
    "auth.signingIn": "Signing in...",
    "generic.operationFailed": "Operation failed",
    "generic.close": "Close",
    "confirm.accept": "Confirm",
    "confirm.cancel": "Cancel",
    "confirm.deleteAccept": "Delete",
    "evidence.visual": "visual",
    "evidence.text": "text",
    "evidence.visualPreview": "Visual preview",
    "evidence.page": (page) => ` - page ${page}`,
    "evidence.preview": "Preview",
    "evidence.openFile": "Open file",
    "status.queued": "queued",
    "status.processing": "processing",
    "status.ready": "ready",
    "status.error": "error",
  },
};

let currentUser = null;
let currentLanguage = "it";
let currentView = "search";
let lastResults = [];
let lastQuery = "";
let hasSearched = false;
let searchState = "idle";
let lastSearchError = "";
let currentProjects = [];
let archiveQuery = "";
let selectedProject = null;
let currentUsers = [];
let projectPage = 1;
let assetPage = 1;
let usersPage = 1;
const expandedUserIds = new Set();
let projectPoll = null;
let sidebarCollapsed = localStorage.getItem("vortex_sidebar_collapsed") === "1";

function t(key, ...args) {
  const value = translations[currentLanguage][key] ?? translations.it[key] ?? key;
  return typeof value === "function" ? value(...args) : value;
}

const confirmModal = document.querySelector("#confirm-modal");
const confirmModalTitle = document.querySelector("#confirm-modal-title");
const confirmModalMessage = document.querySelector("#confirm-modal-message");
const confirmModalAccept = document.querySelector("#confirm-modal-accept");
const confirmModalCancel = document.querySelector("#confirm-modal-cancel");
let confirmModalResolver = null;
let confirmModalLastFocus = null;

function closeConfirmDialog(result) {
  if (!confirmModal || confirmModal.classList.contains("hidden")) {
    return;
  }
  confirmModal.classList.add("hidden");
  document.body.style.overflow = "";
  if (confirmModalLastFocus && typeof confirmModalLastFocus.focus === "function") {
    confirmModalLastFocus.focus();
  }
  confirmModalLastFocus = null;
  const resolve = confirmModalResolver;
  confirmModalResolver = null;
  if (resolve) {
    resolve(result);
  }
}

function confirmDialog({ title, message, confirmLabel, cancelLabel, tone = "danger" } = {}) {
  if (!confirmModal) {
    return Promise.resolve(window.confirm(message || title || ""));
  }
  if (confirmModalResolver) {
    closeConfirmDialog(false);
  }
  confirmModalTitle.textContent = title || "";
  confirmModalMessage.textContent = message || "";
  confirmModalAccept.textContent = confirmLabel || t("confirm.accept");
  confirmModalCancel.textContent = cancelLabel || t("confirm.cancel");
  confirmModalAccept.classList.toggle("is-neutral", tone !== "danger");
  confirmModalLastFocus = document.activeElement;
  confirmModal.classList.remove("hidden");
  document.body.style.overflow = "hidden";
  setTimeout(() => confirmModalAccept.focus(), 0);
  return new Promise((resolve) => {
    confirmModalResolver = resolve;
  });
}

confirmModal?.addEventListener("click", (event) => {
  const action = event.target.closest("[data-confirm-action]")?.dataset.confirmAction;
  if (!action) return;
  closeConfirmDialog(action === "accept");
});

document.addEventListener("keydown", (event) => {
  if (!confirmModal || confirmModal.classList.contains("hidden")) return;
  if (event.key === "Escape") {
    event.preventDefault();
    closeConfirmDialog(false);
  } else if (event.key === "Enter") {
    event.preventDefault();
    closeConfirmDialog(true);
  }
});

async function requestJson(url, options = {}) {
  const response = await fetch(url, {
    credentials: "same-origin",
    ...options,
    headers: {
      ...(options.body instanceof FormData ? {} : { "Content-Type": "application/json" }),
      ...(options.headers || {}),
    },
  });
  const payload = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(formatErrorDetail(payload.detail) || t("generic.operationFailed"));
  }
  return payload;
}

function formatErrorDetail(detail) {
  if (!detail) return "";
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail)) {
    return detail
      .map((item) => (item && typeof item === "object" ? item.msg || JSON.stringify(item) : String(item)))
      .filter(Boolean)
      .join("; ");
  }
  if (typeof detail === "object") return detail.msg || JSON.stringify(detail);
  return String(detail);
}

async function init() {
  applyLanguage("it");
  try {
    const payload = await requestJson("/api/auth/me");
    showApp(payload.user);
    await loadProjects();
  } catch {
    showLogin();
  }
}

function showLogin() {
  currentUser = null;
  resetSearchState();
  loginScreen.classList.remove("hidden");
  appScreen.classList.add("hidden");
  stopProjectPolling();
  applyLanguage("it");
}

function showApp(user) {
  currentUser = user;
  currentLanguage = user.language || "it";
  loginScreen.classList.add("hidden");
  appScreen.classList.remove("hidden");
  sessionUsername.textContent = user.username;

  const isAdmin = user.role === "admin";
  adminNavButtons().forEach((button) => button.classList.toggle("hidden", !isAdmin));
  document.querySelectorAll(".admin-only").forEach((element) => {
    element.classList.toggle("hidden", !isAdmin);
  });

  applyLanguage(currentLanguage);
  setView("search");
  startProjectPolling();
}

function applyLanguage(language) {
  currentLanguage = language || "it";
  document.documentElement.lang = currentLanguage;

  document.querySelectorAll("[data-i18n]").forEach((element) => {
    element.textContent = t(element.dataset.i18n);
  });
  document.querySelectorAll("[data-i18n-placeholder]").forEach((element) => {
    element.placeholder = t(element.dataset.i18nPlaceholder);
  });
  document.querySelectorAll("[data-i18n-aria]").forEach((element) => {
    element.setAttribute("aria-label", t(element.dataset.i18nAria));
  });
  document.querySelectorAll("[data-language]").forEach((button) => {
    button.classList.toggle("active", button.dataset.language === currentLanguage);
  });

  if (currentUser) {
    sessionRole.textContent = `- ${currentUser.role === "admin" ? t("role.admin") : t("role.user")}`;
  }

  renderSearchState();
  setView(currentView);
  renderProjects(currentProjects);
  renderProjectDetail(selectedProject);
  if (currentUsers.length) {
    renderUsers(currentUsers);
  }
}

function applySidebarState() {
  document.body.classList.toggle("sidebar-collapsed", sidebarCollapsed);
  localStorage.setItem("vortex_sidebar_collapsed", sidebarCollapsed ? "1" : "0");
  if (sidebarToggle) {
    sidebarToggle.dataset.i18nAria = sidebarCollapsed ? "sidebar.open" : "sidebar.close";
    sidebarToggle.setAttribute("aria-label", t(sidebarToggle.dataset.i18nAria));
    sidebarToggle.title = t(sidebarToggle.dataset.i18nAria);
  }
}

loginForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  loginStatus.textContent = t("auth.signingIn");

  try {
    const payload = await requestJson("/api/auth/login", {
      method: "POST",
      body: JSON.stringify({
        username: document.querySelector("#login-username").value.trim(),
        password: document.querySelector("#login-password").value,
      }),
    });
    loginForm.reset();
    loginStatus.textContent = "";
    showApp(payload.user);
    await loadProjects();
  } catch (error) {
    loginStatus.textContent = error.message;
  }
});

logoutButton.addEventListener("click", async () => {
  await requestJson("/api/auth/logout", { method: "POST" }).catch(() => {});
  showLogin();
});

sidebarToggle?.addEventListener("click", () => {
  sidebarCollapsed = !sidebarCollapsed;
  applySidebarState();
});

document.addEventListener("click", async (event) => {
  const languageButton = event.target.closest("[data-language]");
  if (languageButton) {
    await changeLanguage(languageButton.dataset.language);
    return;
  }

  const openProjectButton = event.target.closest("[data-open-project]");
  if (openProjectButton) {
    setView("archive");
    await loadProjects({ refreshDetail: false });
    await loadProjectDetail(openProjectButton.dataset.openProject);
    return;
  }

  const paginationButton = event.target.closest("[data-page-target][data-page-action]");
  if (paginationButton) {
    changePage(paginationButton.dataset.pageTarget, paginationButton.dataset.pageAction);
    return;
  }

  const viewButton = event.target.closest("[data-view]");
  if (!viewButton) {
    return;
  }
  const view = viewButton.dataset.view;
  setView(view);
  if (view === "archive") {
    await loadProjects();
  }
  if (view === "admin") {
    await loadUsers();
  }
});

async function changeLanguage(language) {
  if (!["it", "en"].includes(language)) {
    return;
  }
  applyLanguage(language);
  if (!currentUser) {
    return;
  }
  try {
    const payload = await requestJson("/api/auth/me", {
      method: "PATCH",
      body: JSON.stringify({ language }),
    });
    currentUser = payload.user;
    applyLanguage(payload.user.language);
  } catch (error) {
    console.error(error);
  }
}

function setView(view) {
  const adminOnlyView = ["admin", "create"].includes(view);
  const safeView = adminOnlyView && currentUser?.role !== "admin" ? "search" : view;
  currentView = safeView;
  searchView.classList.toggle("hidden", safeView !== "search");
  archiveView.classList.toggle("hidden", safeView !== "archive");
  createView.classList.toggle("hidden", safeView !== "create");
  adminView.classList.toggle("hidden", safeView !== "admin");

  navButtons().forEach((button) => {
    button.classList.toggle("active", button.dataset.view === safeView);
  });

  viewTitle.textContent = {
    search: t("views.search"),
    archive: t("views.archive"),
    create: t("views.create"),
    admin: t("views.admin"),
  }[safeView];
}

document.querySelectorAll(".upload-form").forEach((form) => {
  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    const status = form.querySelector(".upload-status");
    const formData = new FormData(form);
    status.textContent = t("projects.uploading");

    try {
      const project = await requestJson("/api/projects", {
        method: "POST",
        body: formData,
      });
      form.reset();
      status.textContent = t("projects.uploaded");
      selectedProject = project;
      projectPage = 1;
      assetPage = 1;
      setView("archive");
      await loadProjects({ refreshDetail: false });
      await loadProjectDetail(project.id);
    } catch (error) {
      status.textContent = error.message;
    }
  });
});

function getPagination(items, page, pageSize = PAGE_SIZE) {
  const total = items.length;
  const pageCount = Math.max(1, Math.ceil(total / pageSize));
  const safePage = Math.min(Math.max(Number(page) || 1, 1), pageCount);
  const startIndex = (safePage - 1) * pageSize;
  return {
    items: items.slice(startIndex, startIndex + pageSize),
    page: safePage,
    pageCount,
    total,
    start: total ? startIndex + 1 : 0,
    end: Math.min(startIndex + pageSize, total),
  };
}

function renderPagination(target, pagination) {
  if (pagination.total <= PAGE_SIZE) {
    return "";
  }

  return `
    <nav class="pagination" aria-label="${t("pagination.page", pagination.page, pagination.pageCount)}">
      <p class="pagination-summary">${t("pagination.summary", pagination.start, pagination.end, pagination.total)}</p>
      <div class="pagination-actions">
        <button class="pagination-button" type="button" data-page-target="${target}" data-page-action="prev" ${pagination.page <= 1 ? "disabled" : ""}>
          ${t("pagination.previous")}
        </button>
        <span class="pagination-page">${t("pagination.page", pagination.page, pagination.pageCount)}</span>
        <button class="pagination-button" type="button" data-page-target="${target}" data-page-action="next" ${pagination.page >= pagination.pageCount ? "disabled" : ""}>
          ${t("pagination.next")}
        </button>
      </div>
    </nav>
  `;
}

function changePage(target, action) {
  const delta = action === "next" ? 1 : -1;
  if (target === "projects") {
    projectPage += delta;
    renderProjects(currentProjects);
    return;
  }
  if (target === "assets") {
    assetPage += delta;
    renderProjectDetail(selectedProject);
    return;
  }
  if (target === "users") {
    usersPage += delta;
    renderUsers(currentUsers);
  }
}

async function loadProjects(options = {}) {
  const { refreshDetail = true } = options;
  const payload = await requestJson("/api/projects");
  currentProjects = payload.projects;
  renderProjects(currentProjects);
  if (refreshDetail && selectedProject && currentView === "archive") {
    const stillVisible = currentProjects.some((project) => project.id === selectedProject.id);
    if (stillVisible) {
      await loadProjectDetail(selectedProject.id, { focus: false });
    }
  }
}

function renderProjects(projects) {
  if (!projectCount || !projectsList) {
    return;
  }

  const query = archiveQuery.trim().toLowerCase();
  const filtered = query
    ? projects.filter((project) => {
        const haystack = `${project.title || ""}\n${project.description || ""}`.toLowerCase();
        return haystack.includes(query);
      })
    : projects;

  projectCount.textContent = query
    ? t("projects.filteredCount", filtered.length, projects.length)
    : t("projects.count", projects.length);

  if (!projects.length) {
    projectPage = 1;
    projectsList.innerHTML = `<p class="text-sm text-slate-500">${t("projects.empty")}</p>`;
    selectedProject = null;
    renderProjectDetail(null);
    return;
  }

  if (!filtered.length) {
    projectPage = 1;
    projectsList.innerHTML = `<p class="text-sm text-slate-500">${t("projects.noMatches", archiveQuery.trim())}</p>`;
    return;
  }

  const paginated = getPagination(filtered, projectPage);
  projectPage = paginated.page;

  projectsList.innerHTML = paginated.items
    .map((project) => {
      const status = escapeHtml(project.status);
      const selected = selectedProject?.id === project.id ? "project-card-selected" : "";
      const description = project.description
        ? `<p class="project-list-description">${escapeHtml(project.description)}</p>`
        : "";
      return `
        <button class="project-card ${selected}" data-project-id="${escapeHtml(project.id)}" type="button">
          <div class="project-list-main">
            <div class="min-w-0">
              <strong class="project-list-title" title="${escapeHtml(project.title)}">${escapeHtml(project.title)}</strong>
              ${description}
            </div>
          </div>
          <div class="project-list-meta">
            <span class="status-pill status-${status}">${labelStatus(project.status)}</span>
            <span class="chip">${t("projects.filesCount", project.files_count)}</span>
            <span class="chip">${t("projects.chunksCount", project.chunk_count)}</span>
            <span class="chip">${t("projects.visualsCount", project.visual_count)}</span>
          </div>
        </button>
      `;
    })
    .join("") + renderPagination("projects", paginated);
}

projectsList?.addEventListener("click", async (event) => {
  const card = event.target.closest("[data-project-id]");
  if (!card) {
    return;
  }
  await loadProjectDetail(card.dataset.projectId);
});

archiveFilterInput?.addEventListener("input", (event) => {
  archiveQuery = event.target.value;
  projectPage = 1;
  archiveFilterClear?.classList.toggle("hidden", !archiveQuery.trim());
  renderProjects(currentProjects);
});

archiveFilterClear?.addEventListener("click", () => {
  archiveQuery = "";
  projectPage = 1;
  if (archiveFilterInput) {
    archiveFilterInput.value = "";
    archiveFilterInput.focus();
  }
  archiveFilterClear.classList.add("hidden");
  renderProjects(currentProjects);
});

async function loadProjectDetail(projectId, options = {}) {
  const isNewProject = selectedProject?.id !== projectId;
  const project = await requestJson(`/api/projects/${projectId}`);
  if (isNewProject) {
    assetPage = 1;
  }
  selectedProject = project;
  renderProjects(currentProjects);
  renderProjectDetail(project);
}

function renderProjectDetail(project) {
  if (!projectDetail) {
    return;
  }
  if (!project) {
    assetPage = 1;
    projectDetail.classList.add("hidden");
    projectDetail.innerHTML = "";
    document.body.classList.remove("modal-open");
    return;
  }

  const status = escapeHtml(project.status);
  const description = project.description
    ? `<p class="mt-2 max-w-3xl text-sm leading-6 text-slate-500">${escapeHtml(project.description)}</p>`
    : "";
  const assets = project.assets || [];
  const paginatedAssets = getPagination(assets, assetPage);
  assetPage = paginatedAssets.page;
  const assetsMarkup = assets.length
    ? paginatedAssets.items.map(renderAsset).join("")
    : `<p class="text-sm text-slate-500">${t("projectDetail.noAssets")}</p>`;
  const adminTools =
    currentUser?.role === "admin"
      ? `
        <div class="grid gap-5 border-t border-slate-200 pt-5 lg:grid-cols-2">
          <form class="project-meta-form grid gap-3" data-project-id="${escapeHtml(project.id)}">
            <div>
              <p class="text-xs font-semibold uppercase tracking-[0.18em] text-vortex">${t("projectDetail.metadata")}</p>
            </div>
            <label class="block text-sm font-medium text-slate-700">
              <span>${t("projects.name")}</span>
              <input name="title" class="field mt-2" type="text" value="${escapeHtml(project.title)}" required />
            </label>
            <label class="block text-sm font-medium text-slate-700">
              <span>${t("projects.notes")}</span>
              <textarea name="description" class="field mt-2 min-h-24 py-2" rows="4">${escapeHtml(project.description || "")}</textarea>
            </label>
            <div class="flex flex-wrap items-center gap-3">
              <button class="h-10 rounded-xl bg-slate-950 px-5 font-semibold text-white transition hover:bg-vortex" type="submit">${t("projectDetail.save")}</button>
              <p class="project-meta-status min-h-5 text-sm text-slate-500"></p>
            </div>
          </form>

          <form class="project-add-assets-form grid content-start gap-3" data-project-id="${escapeHtml(project.id)}">
            <div>
              <p class="text-xs font-semibold uppercase tracking-[0.18em] text-vortex">${t("projectDetail.addAssetsTitle")}</p>
              <p class="mt-2 text-sm leading-6 text-slate-500">${t("projectDetail.addAssetsHint")}</p>
            </div>
            <label class="block text-sm font-medium text-slate-700">
              <span>${t("projectDetail.selectFiles")}</span>
              <input name="files" class="field mt-2 h-auto py-2" type="file" multiple required />
            </label>
            <div class="flex flex-wrap items-center gap-3">
              <button class="h-10 rounded-xl bg-slate-950 px-5 font-semibold text-white transition hover:bg-vortex" type="submit">${t("projectDetail.addAssets")}</button>
              <p class="project-add-assets-status min-h-5 text-sm text-slate-500"></p>
            </div>
          </form>
        </div>

        <div class="mt-5 flex flex-wrap items-center justify-between gap-3 rounded-2xl border border-red-100 bg-red-50/50 px-4 py-3">
          <div class="min-w-0">
            <p class="text-xs font-semibold uppercase tracking-[0.18em] text-red-700">${t("projectDetail.dangerZone")}</p>
            <p class="mt-1 text-sm text-slate-600">${t("projectDetail.deleteHint")}</p>
          </div>
          <button class="project-delete inline-flex h-10 items-center gap-2 rounded-xl border border-red-200 bg-white px-4 font-semibold text-red-700 transition hover:border-red-400 hover:bg-red-50" type="button" data-project-id="${escapeHtml(project.id)}" data-project-title="${escapeHtml(project.title)}">
            <svg class="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
              <path d="M4 7h16"/><path d="M10 7V4h4v3"/><path d="M6 7l1 13h10l1-13"/><path d="M10 11v6"/><path d="M14 11v6"/>
            </svg>
            <span>${t("projectDetail.delete")}</span>
          </button>
        </div>
      `
      : "";

  projectDetail.classList.remove("hidden");
  document.body.classList.add("modal-open");
  projectDetail.innerHTML = `
    <div class="project-detail-modal" role="dialog" aria-modal="true" aria-labelledby="project-detail-title">
      <button class="project-detail-close" type="button" aria-label="${t("generic.close")}" title="${t("generic.close")}">
        <svg viewBox="0 0 24 24" fill="none" aria-hidden="true">
          <path d="M6 6l12 12"/><path d="M18 6l-12 12"/>
        </svg>
      </button>
      <div class="mb-5 flex flex-wrap items-start justify-between gap-3 pr-12">
        <div class="min-w-0">
          <p class="text-xs font-semibold uppercase tracking-[0.18em] text-vortex">${t("projectDetail.eyebrow")}</p>
          <h3 id="project-detail-title" class="mt-1 text-xl font-semibold tracking-tight">${escapeHtml(project.title)}</h3>
          ${description}
        </div>
        <span class="status-pill status-${status}">${labelStatus(project.status)}</span>
      </div>
      <div class="mb-5 flex flex-wrap gap-1.5">
        <span class="chip">${t("projects.filesCount", project.files_count)}</span>
        <span class="chip">${t("projects.chunksCount", project.chunk_count)}</span>
        <span class="chip">${t("projects.visualsCount", project.visual_count)}</span>
      </div>
      <div class="grid gap-5">
        <section>
          <h4 class="mb-2 text-sm font-bold uppercase tracking-[0.16em] text-slate-500">${t("projectDetail.assets")}</h4>
          <div class="grid gap-3">${assetsMarkup}</div>
          ${renderPagination("assets", paginatedAssets)}
        </section>
        ${adminTools}
      </div>
    </div>
  `;
}

function closeProjectDetail() {
  selectedProject = null;
  renderProjectDetail(null);
  renderProjects(currentProjects);
}

function renderAsset(asset) {
  const assetId = escapeHtml(asset.id);
  const status = escapeHtml(asset.status);
  const previewLink = asset.preview_path
    ? `<a class="asset-action" href="/api/assets/${assetId}/preview" target="_blank" rel="noreferrer">${t("projectDetail.preview")}</a>`
    : "";
  const pageChip = asset.page_count ? `<span class="chip">${t("projectDetail.pages", asset.page_count)}</span>` : "";
  const visualCaption = asset.visual_caption
    ? `<p class="mt-2 text-xs leading-5 text-slate-600">${escapeHtml(asset.visual_caption)}</p>`
    : "";
  const visualTags = asset.visual_tags
    ? String(asset.visual_tags)
        .split(",")
        .map((tag) => tag.trim())
        .filter(Boolean)
        .slice(0, 6)
        .map((tag) => `<span class="chip">${escapeHtml(tag)}</span>`)
        .join("")
    : "";
  const visualTagsMarkup = visualTags ? `<div class="mt-2 flex flex-wrap gap-1.5">${visualTags}</div>` : "";
  const error = asset.error ? `<p class="mt-2 line-clamp-2 text-xs leading-5 text-red-600">${escapeHtml(asset.error)}</p>` : "";

  return `
    <article class="asset-row">
      <div class="thumb-wrap asset-thumb" data-kind="${labelAssetKind(asset)}">
        <img class="thumb" src="/api/assets/${assetId}/preview" alt="" onerror="this.remove()" />
      </div>
      <div class="min-w-0">
        <div class="mb-2 flex flex-wrap items-center gap-2">
          <strong class="truncate text-sm" title="${escapeHtml(asset.filename)}">${escapeHtml(asset.filename)}</strong>
          <span class="status-pill status-${status}">${labelStatus(asset.status)}</span>
        </div>
        <p class="truncate text-xs text-slate-500">${escapeHtml(asset.content_type)}</p>
        <div class="mt-2 flex flex-wrap gap-1.5">
          ${pageChip}
          <span class="chip">${t("projectDetail.assetStats", asset.chunk_count, asset.visual_count)}</span>
        </div>
        ${visualCaption}
        ${visualTagsMarkup}
        ${error}
      </div>
      <div class="asset-actions">
        ${previewLink}
        <a class="asset-action" href="/api/assets/${assetId}/download">${t("projectDetail.download")}</a>
      </div>
    </article>
  `;
}

function labelAssetKind(asset) {
  const contentType = asset.content_type || "";
  if (contentType.includes("pdf")) {
    return "pdf";
  }
  if (contentType.startsWith("image/")) {
    return "image";
  }
  if (contentType.startsWith("text/")) {
    return "text";
  }
  return "file";
}

projectDetail?.addEventListener("submit", async (event) => {
  const metaForm = event.target.closest(".project-meta-form");
  const addAssetsForm = event.target.closest(".project-add-assets-form");

  if (metaForm) {
    event.preventDefault();
    const status = metaForm.querySelector(".project-meta-status");
    status.textContent = t("projectDetail.saving");
    try {
      const payload = await requestJson(`/api/projects/${metaForm.dataset.projectId}`, {
        method: "PATCH",
        body: JSON.stringify({
          title: metaForm.elements.title.value.trim(),
          description: metaForm.elements.description.value.trim(),
        }),
      });
      selectedProject = payload;
      await loadProjects({ refreshDetail: false });
      renderProjectDetail(payload);
      projectDetail.querySelector(".project-meta-status").textContent = t("projectDetail.saved");
    } catch (error) {
      status.textContent = error.message;
    }
    return;
  }

  if (addAssetsForm) {
    event.preventDefault();
    const status = addAssetsForm.querySelector(".project-add-assets-status");
    const formData = new FormData(addAssetsForm);
    status.textContent = t("projectDetail.addingAssets");
    try {
      const payload = await requestJson(`/api/projects/${addAssetsForm.dataset.projectId}/assets`, {
        method: "POST",
        body: formData,
      });
      selectedProject = payload;
      await loadProjects({ refreshDetail: false });
      renderProjectDetail(payload);
      projectDetail.querySelector(".project-add-assets-status").textContent = t("projectDetail.assetsAdded");
    } catch (error) {
      status.textContent = error.message;
    }
    return;
  }

});

projectDetail?.addEventListener("click", async (event) => {
  if (event.target === projectDetail || event.target.closest(".project-detail-close")) {
    closeProjectDetail();
    return;
  }

  const deleteButton = event.target.closest(".project-delete");
  if (!deleteButton) {
    return;
  }
  const projectId = deleteButton.dataset.projectId;
  const projectTitle = deleteButton.dataset.projectTitle || "";
  const ok = await confirmDialog({
    title: t("projectDetail.delete"),
    message: t("projectDetail.confirmDelete", projectTitle),
    confirmLabel: t("confirm.deleteAccept"),
    cancelLabel: t("confirm.cancel"),
  });
  if (!ok) {
    return;
  }
  const originalLabel = deleteButton.querySelector("span")?.textContent;
  deleteButton.disabled = true;
  if (deleteButton.querySelector("span")) {
    deleteButton.querySelector("span").textContent = t("projectDetail.deleting");
  }
  try {
    await requestJson(`/api/projects/${projectId}`, { method: "DELETE" });
    selectedProject = null;
    renderProjectDetail(null);
    await loadProjects({ refreshDetail: false });
  } catch (error) {
    window.alert(error.message);
    deleteButton.disabled = false;
    if (deleteButton.querySelector("span") && originalLabel) {
      deleteButton.querySelector("span").textContent = originalLabel;
    }
  }
});

document.addEventListener("keydown", (event) => {
  if (event.key === "Escape" && projectDetail && !projectDetail.classList.contains("hidden")) {
    closeProjectDetail();
  }
});

searchForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const query = searchQuery.value.trim();
  if (query.length < 2) {
    return;
  }

  hasSearched = true;
  searchState = "searching";
  lastQuery = query;
  lastResults = [];
  lastSearchError = "";
  renderSearchState();

  try {
    const payload = await requestJson("/api/search", {
      method: "POST",
      body: JSON.stringify({
        query,
        mode: "all",
        limit: PAGE_SIZE,
      }),
    });
    lastResults = payload.results;
    searchState = "done";
    renderSearchState();
  } catch (error) {
    lastResults = [];
    lastSearchError = error.message;
    searchState = "error";
    renderSearchState();
  }
});

function renderSearchState() {
  if (!hasSearched) {
    resultsPanel?.classList.add("hidden");
    return;
  }

  resultsPanel?.classList.remove("hidden");
  if (searchState === "searching") {
    resultsSummary.textContent = t("results.searching");
    results.innerHTML = emptyState(t("results.searchingBody"));
    return;
  }

  if (searchState === "error") {
    resultsSummary.textContent = t("results.error");
    results.innerHTML = emptyState(lastSearchError || t("generic.operationFailed"));
    return;
  }

  renderResults(lastResults, lastQuery);
}

function resetSearchState() {
  hasSearched = false;
  searchState = "idle";
  lastQuery = "";
  lastResults = [];
  lastSearchError = "";
  resultsPanel?.classList.add("hidden");
  if (results) {
    results.innerHTML = "";
  }
}

function renderResults(items, query) {
  if (!items.length) {
    resultsSummary.textContent = t("results.none");
    results.innerHTML = emptyState(t("results.noneBody", query));
    return;
  }

  resultsSummary.textContent = t("results.count", items.length);
  results.innerHTML = `
    <div class="grid gap-3">
      ${items.map(renderResult).join("")}
    </div>
  `;
}

function renderResult(item) {
  const score = Math.max(0, item.score || 0).toFixed(3);
  const description = item.description
    ? `<p class="mt-1 max-w-3xl text-sm leading-6 text-slate-500">${escapeHtml(item.description)}</p>`
    : "";

  return `
    <article class="result-card">
      <div class="flex flex-wrap items-start justify-between gap-3">
        <div>
          <h2 class="text-lg font-semibold tracking-tight">${escapeHtml(item.title)}</h2>
          ${description}
        </div>
        <div class="flex flex-wrap items-center gap-2">
          <button class="rounded-full bg-slate-950 px-3 py-1 text-sm font-bold text-white transition hover:bg-vortex" data-open-project="${escapeHtml(item.project_id)}" type="button">${t("projectDetail.open")}</button>
          <div class="rounded-full bg-teal-50 px-3 py-1 text-sm font-bold text-vortex">${score}</div>
        </div>
      </div>
      <div class="grid gap-3">
        ${(item.evidence || []).map(renderEvidence).join("")}
      </div>
    </article>
  `;
}

function renderEvidence(evidence) {
  const page = evidence.page ? t("evidence.page", evidence.page) : "";
  const kind = evidence.kind === "visual" ? t("evidence.visual") : t("evidence.text");
  const snippet = evidence.kind === "visual"
    ? escapeHtml(evidence.snippet || t("evidence.visualPreview"))
    : escapeHtml(evidence.snippet || "");
  const actionUrl = evidence.preview_available ? evidence.preview_url : evidence.download_url;
  const actionLabel = evidence.preview_available ? t("evidence.preview") : t("evidence.openFile");
  const actionTarget = evidence.preview_available ? ` target="_blank" rel="noreferrer"` : "";

  return `
    <div class="evidence-card">
      <div class="thumb-wrap" data-kind="${kind}">
        <img class="thumb" src="${evidence.preview_url}" alt="" onerror="this.remove()" />
      </div>
      <div class="min-w-0">
        <div class="mb-2 flex flex-wrap items-center gap-2 text-sm font-semibold">
          <span class="rounded-full ${evidence.kind === "visual" ? "bg-amber-100 text-amber-700" : "bg-teal-100 text-vortex"} px-2 py-1 text-xs uppercase">${kind}</span>
          <span class="truncate">${escapeHtml(evidence.filename || "file")}${page}</span>
        </div>
        <p class="line-clamp-3 text-sm leading-6 text-slate-600">${snippet}</p>
        <a class="mt-2 inline-flex text-sm font-semibold text-vortex hover:underline" href="${actionUrl}"${actionTarget}>${actionLabel}</a>
      </div>
    </div>
  `;
}

userForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  userFormStatus.textContent = t("accounts.creating");

  try {
    await requestJson("/api/users", {
      method: "POST",
      body: JSON.stringify({
        username: document.querySelector("#new-username").value.trim(),
        password: document.querySelector("#new-password").value,
        role: document.querySelector("#new-role").value,
        language: "it",
      }),
    });
    userForm.reset();
    userFormStatus.textContent = t("accounts.created");
    await loadUsers();
  } catch (error) {
    userFormStatus.textContent = error.message;
  }
});

async function loadUsers() {
  if (!currentUser || currentUser.role !== "admin") {
    return;
  }
  const payload = await requestJson("/api/users");
  currentUsers = payload.users;
  const stillPresent = new Set(currentUsers.map((u) => u.id));
  for (const id of [...expandedUserIds]) {
    if (!stillPresent.has(id)) expandedUserIds.delete(id);
  }
  renderUsers(currentUsers);
}

function renderUsers(users) {
  if (!usersList) {
    return;
  }

  if (!users.length) {
    usersPage = 1;
    usersList.innerHTML = "";
    return;
  }

  const paginated = getPagination(users, usersPage);
  usersPage = paginated.page;

  usersList.innerHTML = paginated.items
    .map((user) => {
      const isSelf = user.id === currentUser?.id;
      const initial = (user.username || "?").trim().charAt(0).toUpperCase();
      const isAdmin = user.role === "admin";
      return `
        <article class="user-card ${isSelf ? "user-card-self" : ""} ${expandedUserIds.has(user.id) ? "is-expanded" : ""}" data-user-id="${escapeHtml(user.id)}">
          <button type="button" class="user-card-header user-card-toggle" aria-expanded="${expandedUserIds.has(user.id) ? "true" : "false"}">
            <div class="user-avatar ${isAdmin ? "user-avatar-admin" : ""}" aria-hidden="true">${escapeHtml(initial)}</div>
            <div class="user-headline">
              <span class="user-headline-name">${escapeHtml(user.username)}</span>
              <div class="user-headline-meta">
                <span class="user-tag user-tag-role-${isAdmin ? "admin" : "user"}">${escapeHtml(isAdmin ? t("role.admin") : t("role.user"))}</span>
                <span class="user-tag ${user.active ? "user-tag-active" : "user-tag-disabled"}">${user.active ? t("accounts.active") : t("accounts.disabled")}</span>
                <span class="user-tag">${escapeHtml((user.language || "it").toUpperCase())}</span>
                ${isSelf ? `<span class="user-tag user-tag-self">${t("accounts.youTag")}</span>` : ""}
              </div>
            </div>
            <span class="user-card-chevron" aria-hidden="true">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round">
                <path d="M6 9l6 6 6-6"/>
              </svg>
            </span>
          </button>

          <div class="user-card-body">
            <div class="user-field">
              <span class="user-field-label">${t("accounts.roleLabel")}</span>
              <select class="user-role field">
                <option value="user" ${user.role === "user" ? "selected" : ""}>${t("role.user")}</option>
                <option value="admin" ${user.role === "admin" ? "selected" : ""}>${t("role.admin")}</option>
              </select>
            </div>
            <div class="user-field">
              <span class="user-field-label">${t("accounts.statusLabel")}</span>
              <label class="user-toggle">
                <input class="user-active" type="checkbox" ${user.active ? "checked" : ""} />
                <span>${user.active ? t("accounts.active") : t("accounts.disabled")}</span>
              </label>
            </div>
            <div class="user-field">
              <span class="user-field-label">${t("accounts.languageLabel")}</span>
              <select class="user-language field">
                <option value="it" ${user.language === "it" ? "selected" : ""}>Italiano</option>
                <option value="en" ${user.language === "en" ? "selected" : ""}>English</option>
              </select>
            </div>
            <div class="user-field" style="grid-column: 1 / -1;">
              <span class="user-field-label">${t("accounts.passwordLabel")}</span>
              <input class="user-password field" type="password" placeholder="${t("accounts.newPassword")}" autocomplete="new-password" />
            </div>
          </div>

          <div class="user-card-actions">
            <button class="user-delete user-action user-action-delete" type="button" ${isSelf ? "disabled" : ""} title="${isSelf ? t("accounts.cannotDeleteSelf") : t("accounts.delete")}">
              <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 7h16"/><path d="M10 7V4h4v3"/><path d="M6 7l1 13h10l1-13"/><path d="M10 11v6"/><path d="M14 11v6"/></svg>
              ${t("accounts.delete")}
            </button>
            <button class="user-save user-action user-action-save" type="button">
              <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 12l5 5 9-11"/></svg>
              ${t("accounts.save")}
            </button>
          </div>
        </article>
      `;
    })
    .join("") + renderPagination("users", paginated);
}

usersList.addEventListener("click", async (event) => {
  const toggle = event.target.closest(".user-card-toggle");
  if (toggle) {
    const card = toggle.closest("[data-user-id]");
    if (card) {
      const userId = card.dataset.userId;
      const willExpand = !expandedUserIds.has(userId);
      if (willExpand) {
        expandedUserIds.add(userId);
      } else {
        expandedUserIds.delete(userId);
      }
      card.classList.toggle("is-expanded", willExpand);
      toggle.setAttribute("aria-expanded", willExpand ? "true" : "false");
    }
    return;
  }

  const saveButton = event.target.closest(".user-save");
  const deleteButton = event.target.closest(".user-delete");
  const button = saveButton || deleteButton;
  if (!button) {
    return;
  }

  const row = button.closest("[data-user-id]");

  if (deleteButton) {
    const username = row.querySelector(".user-headline-name")?.textContent?.trim() || "";
    const ok = await confirmDialog({
      title: t("accounts.delete"),
      message: t("accounts.confirmDelete", username),
      confirmLabel: t("confirm.deleteAccept"),
      cancelLabel: t("confirm.cancel"),
    });
    if (!ok) {
      return;
    }
    deleteButton.disabled = true;
    deleteButton.textContent = t("accounts.deleting");
    try {
      await requestJson(`/api/users/${row.dataset.userId}`, { method: "DELETE" });
      userFormStatus.textContent = t("accounts.deleted");
      await loadUsers();
    } catch (error) {
      userFormStatus.textContent = error.message;
      deleteButton.disabled = false;
      deleteButton.textContent = t("accounts.delete");
    }
    return;
  }

  const password = row.querySelector(".user-password").value;
  saveButton.textContent = t("accounts.saving");

  try {
    await requestJson(`/api/users/${row.dataset.userId}`, {
      method: "PATCH",
      body: JSON.stringify({
        role: row.querySelector(".user-role").value,
        active: row.querySelector(".user-active").checked,
        language: row.querySelector(".user-language").value,
        password: password || null,
      }),
    });
    userFormStatus.textContent = t("accounts.updated");
    await loadUsers();
  } catch (error) {
    userFormStatus.textContent = error.message;
    saveButton.textContent = t("accounts.save");
  }
});

function startProjectPolling() {
  if (!projectPoll) {
    projectPoll = setInterval(() => loadProjects().catch(() => {}), 3000);
  }
}

function stopProjectPolling() {
  if (projectPoll) {
    clearInterval(projectPoll);
    projectPoll = null;
  }
}

function emptyState(message) {
  return `
    <div class="grid min-h-80 place-items-center rounded-3xl border border-dashed border-slate-200 bg-slate-50 p-6 text-center">
      <div>
        <img class="mx-auto mb-4 h-12 w-12 rounded-2xl" src="/vortex-icon.svg" alt="" />
        <p class="mx-auto max-w-sm text-sm leading-6 text-slate-500">${escapeHtml(message)}</p>
      </div>
    </div>
  `;
}

function labelStatus(status) {
  return t(`status.${status}`);
}

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

applySidebarState();
init();
