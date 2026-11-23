function loadFeed() {
    console.log("Feed loaded");
    document.querySelector(".feed-item-content").innerHTML = "Feed loaded";
    window.location.href = "categories.html";
}

function loadCategories() {
    console.log("Categories loaded");
    document.querySelector(".categories-content").innerHTML = "Categories loaded";
    window.location.href = "categories.html";
}


const LIMIT = 5;
let offset = 0;
let loading = false;
let done = false;

const container = document.getElementById("feed-container");
const template = document.getElementById("news-template");
const scrollBox = document.getElementById("feed-scroll");
const sentinel = document.getElementById("feed-sentinel");

function sentinelIsVisible() {
  const root = scrollBox.getBoundingClientRect();
  const mark = sentinel.getBoundingClientRect();
  return mark.top <= root.bottom + 200;
}

async function loadFeedItems() {
  if (loading || done) return;
  loading = true;

  try {
    const response = await fetch(`/articles/${LIMIT}/${offset}`);
    if (!response.ok) throw new Error(`Request failed: ${response.status}`);

    const articles = await response.json();
    if (!Array.isArray(articles)) throw new Error("Unexpected response");

    if (offset === 0) container.innerHTML = "";

    if (articles.length === 0) {
      done = true;
      if (offset === 0) container.innerHTML = "<p>Artikleid ei leitud.</p>";
      return;
    }

    for (const article of articles) {
      const clone = template.content.cloneNode(true);
      clone.querySelector(".news-date").textContent = article.published || "";
      clone.querySelector(".news-author").textContent = article.author || "";
      clone.querySelector(".news-source").textContent = article.source || "";
      clone.querySelector(".news-title").textContent = article.title || "";
      clone.querySelector(".news-body").textContent = article.summary || "";
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
