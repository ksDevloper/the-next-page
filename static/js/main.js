/**
 * THE NEXT PAGE INTERACTION SCRIPTS
 * Live filtering, sorting, typeahead autocomplete, and book summary modal.
 */

document.addEventListener("DOMContentLoaded", function () {
  initGenreFilters();
  initAutocomplete();
  initKeyboardShortcuts();
});

/* ==========================================================================
   1. Filter & Sort on Popular Books (Page 1)
   ========================================================================== */

let currentGenreFilter = "all";
let currentSearchQuery = "";

function initGenreFilters() {
  const filterBtns = document.querySelectorAll("#genreFilterGroup .filter-pill");
  if (!filterBtns.length) return;

  filterBtns.forEach(btn => {
    btn.addEventListener("click", function () {
      filterBtns.forEach(b => b.classList.remove("active"));
      this.classList.add("active");
      currentGenreFilter = this.getAttribute("data-filter").toLowerCase();
      renderFilteredBooks();
    });
  });
}

function applyTitleFilter() {
  const input = document.getElementById("popularSearchInput");
  if (!input) return;
  currentSearchQuery = input.value.trim().toLowerCase();
  renderFilteredBooks();
}

function renderFilteredBooks() {
  const cards = document.querySelectorAll("#popularBooksGrid .book-card");
  const noResults = document.getElementById("noResultsNotice");
  let visibleCount = 0;

  cards.forEach(card => {
    const cardTitle = card.getAttribute("data-title") || "";
    const cardAuthor = card.getAttribute("data-author") || "";
    const cardGenre = card.getAttribute("data-genre") || "";

    const matchesGenre = currentGenreFilter === "all" || cardGenre.includes(currentGenreFilter);
    const matchesSearch = !currentSearchQuery || 
                          cardTitle.includes(currentSearchQuery) || 
                          cardAuthor.includes(currentSearchQuery);

    if (matchesGenre && matchesSearch) {
      card.style.display = "flex";
      visibleCount++;
    } else {
      card.style.display = "none";
    }
  });

  if (noResults) {
    noResults.style.display = visibleCount === 0 ? "block" : "none";
  }
}

function applySorting() {
  const select = document.getElementById("sortSelect");
  const grid = document.getElementById("popularBooksGrid");
  if (!select || !grid) return;

  const cards = Array.from(grid.querySelectorAll(".book-card"));
  const sortValue = select.value;

  cards.sort((a, b) => {
    if (sortValue === "rating-desc") {
      return parseFloat(b.dataset.rating) - parseFloat(a.dataset.rating);
    } else if (sortValue === "reviews-desc") {
      return parseInt(b.dataset.reviews) - parseInt(a.dataset.reviews);
    } else if (sortValue === "ratings-desc") {
      return parseInt(b.dataset.totalratings) - parseInt(a.dataset.totalratings);
    } else if (sortValue === "title-asc") {
      return a.dataset.title.localeCompare(b.dataset.title);
    }
    return 0;
  });

  cards.forEach(card => grid.appendChild(card));
}

/* ==========================================================================
   2. Autocomplete Suggestions (Page 2)
   ========================================================================== */

let debounceTimer = null;
let currentHighlightedIndex = -1;

function initAutocomplete() {
  const input = document.getElementById("bookQueryInput");
  const dropdown = document.getElementById("autocompleteDropdown");
  if (!input || !dropdown) return;

  input.addEventListener("input", function () {
    clearTimeout(debounceTimer);
    const query = this.value.trim();

    if (query.length < 2) {
      dropdown.innerHTML = "";
      dropdown.classList.remove("open");
      return;
    }

    debounceTimer = setTimeout(() => {
      fetch(`/api/autocomplete?q=${encodeURIComponent(query)}`)
        .then(res => res.json())
        .then(data => {
          renderAutocomplete(data, dropdown, input);
        })
        .catch(err => {
          console.error("Autocomplete error:", err);
          dropdown.classList.remove("open");
        });
    }, 150);
  });

  // Handle keyboard navigation in autocomplete
  input.addEventListener("keydown", function (e) {
    const items = dropdown.querySelectorAll(".autocomplete-item");
    if (!dropdown.classList.contains("open") || !items.length) return;

    if (e.key === "ArrowDown") {
      e.preventDefault();
      currentHighlightedIndex = (currentHighlightedIndex + 1) % items.length;
      updateHighlight(items);
    } else if (e.key === "ArrowUp") {
      e.preventDefault();
      currentHighlightedIndex = (currentHighlightedIndex - 1 + items.length) % items.length;
      updateHighlight(items);
    } else if (e.key === "Enter" && currentHighlightedIndex >= 0) {
      e.preventDefault();
      items[currentHighlightedIndex].click();
    } else if (e.key === "Escape") {
      dropdown.classList.remove("open");
    }
  });

  // Close dropdown on outside click
  document.addEventListener("click", function (e) {
    if (!input.contains(e.target) && !dropdown.contains(e.target)) {
      dropdown.classList.remove("open");
    }
  });
}

function renderAutocomplete(data, dropdown, input) {
  dropdown.innerHTML = "";
  currentHighlightedIndex = -1;

  if (!data || !data.length) {
    dropdown.classList.remove("open");
    return;
  }

  data.forEach(book => {
    const item = document.createElement("div");
    item.className = "autocomplete-item";
    item.innerHTML = `
      <span class="autocomplete-title">${escapeHtml(book.title)}</span>
      <span class="autocomplete-author">${escapeHtml(book.author)}</span>
    `;

    item.addEventListener("click", function () {
      input.value = book.title;
      dropdown.classList.remove("open");
      document.getElementById("searchForm").submit();
    });

    dropdown.appendChild(item);
  });

  dropdown.classList.add("open");
}

function updateHighlight(items) {
  items.forEach((item, idx) => {
    if (idx === currentHighlightedIndex) {
      item.classList.add("selected");
      item.scrollIntoView({ block: "nearest" });
    } else {
      item.classList.remove("selected");
    }
  });
}

function selectSample(title) {
  const input = document.getElementById("bookQueryInput");
  const form = document.getElementById("searchForm");
  if (input && form) {
    input.value = title;
    form.submit();
  }
}

/* ==========================================================================
   3. Book Summary Modal
   ========================================================================== */

function getModalElement() {
  return document.getElementById("summaryModal") || document.getElementById("curatorModal");
}

function openBookSummary(title, author, rating, readersText, isbn, desc) {
  const modal = getModalElement();
  if (!modal) return;

  const titleEl = document.getElementById("modalTitle");
  const authorEl = document.getElementById("modalAuthor");
  const ratingEl = document.getElementById("modalRating");
  const reviewsEl = document.getElementById("modalReviews");
  const isbnEl = document.getElementById("modalIsbn");
  const descEl = document.getElementById("modalDesc");

  if (titleEl) titleEl.textContent = title;
  if (authorEl) authorEl.textContent = "by " + author;
  if (ratingEl) ratingEl.textContent = rating ? `★ ${rating}` : "N/A";
  if (reviewsEl) reviewsEl.textContent = readersText || "—";
  if (isbnEl) isbnEl.textContent = isbn || "Not Available";
  if (descEl) descEl.textContent = desc || "No summary available for this book.";

  modal.classList.add("open");
  document.body.style.overflow = "hidden";
}

// Alias for compatibility
function openCuratorSlip(title, author, rating, readersText, isbn, desc) {
  openBookSummary(title, author, rating, readersText, isbn, desc);
}

function closeBookSummary() {
  const modal = getModalElement();
  if (!modal) return;
  modal.classList.remove("open");
  document.body.style.overflow = "";
}

// Alias for compatibility
function closeCuratorSlip() {
  closeBookSummary();
}

function handleBackdropClick(e) {
  const modal = getModalElement();
  if (modal && e.target === modal) {
    closeBookSummary();
  }
}

function initKeyboardShortcuts() {
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape") {
      closeBookSummary();
    }
  });
}

/* ==========================================================================
   4. Image Error Fallback Handler
   ========================================================================== */

function handleImageError(imgEl, title, author) {
  const wrap = imgEl.parentElement;
  if (!wrap) return;

  const fallback = document.createElement("div");
  fallback.className = "book-cover-fallback";
  fallback.style.width = imgEl.style.width || "100%";
  fallback.style.height = imgEl.style.height || "100%";
  fallback.style.maxHeight = "280px";
  fallback.innerHTML = `
    <div class="fallback-title">${escapeHtml(title)}</div>
    <div class="fallback-author">${escapeHtml(author)}</div>
  `;

  imgEl.remove();
  wrap.appendChild(fallback);
}

function escapeHtml(str) {
  if (!str) return "";
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}
