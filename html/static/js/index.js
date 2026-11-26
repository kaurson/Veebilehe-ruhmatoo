

const LIMIT = 5;
let offset = 0;
let loading = false;
let done = false;

const container = document.getElementById("feed-container");
const template = document.getElementById("news-template");
const scrollBox = document.getElementById("feed-scroll");
const sentinel = document.getElementById("feed-sentinel");

// Kirjutab valitud elemendi teksti.
function setText(root, selector, value) {
  const node = root.querySelector(selector);
  if (node) node.textContent = value || "";
}

// Kontrollib, kas voo lõpp on ekraanil näha.
function sentinelIsVisible() {
  const root = scrollBox.getBoundingClientRect();
  const mark = sentinel.getBoundingClientRect();
  return mark.top <= root.bottom + 200;
}

// Laeb serverist järgmise hulga artikleid ja lisab need voogu.
async function loadFeedItems() {
  if (window.feedPaused || loading || done) return;
  loading = true;

  try {
    const response = await fetch(`/articles/${LIMIT}/${offset}`);
    const articles = await response.json();
    if (window.feedPaused) return;
    if (!response.ok) throw new Error(`Request failed: ${response.status}`);
    if (!Array.isArray(articles)) throw new Error("Unexpected response");

    if (offset === 0) container.innerHTML = "";

    if (articles.length === 0) {
      done = true;
      if (offset === 0) container.innerHTML = "<p>Artikleid ei leitud.</p>";
      return;
    }

    for (const article of articles) {
      const clone = template.content.cloneNode(true);
      setText(clone, ".news-date", article.published);
      setText(clone, ".news-author", article.author);
      setText(clone, ".news-source", article.source);
      setText(clone, ".news-title", article.title);
      const link = clone.querySelector(".news-link");
      if (link && article.link) link.href = article.link;
      container.appendChild(clone);
    }

    offset += articles.length;
    if (articles.length < LIMIT) done = true;
  } catch (error) {
    console.error("Error loading news:", error);
    done = true;
    if (offset === 0) container.innerHTML = "<p>Failed to load news feed.</p>";
  } finally {
    loading = false;
  }
}

// Laeb artikleid seni, kuni voog täidab nähtava ala.
async function loadUntilFilled() {
  while (!done && sentinelIsVisible()) {
    const loaded = offset;
    await loadFeedItems();
    if (offset === loaded) break;
  }
}

const observer = new IntersectionObserver(
  (entries) => {
    if (entries.some((entry) => entry.isIntersecting)) loadUntilFilled();
  },
  { root: scrollBox, rootMargin: "200px" }
);

observer.observe(sentinel);
loadUntilFilled();
