(() => {
    const grid = document.getElementById("category-grid");
    const container = document.getElementById("feed-container");
    const template = document.getElementById("news-template");
    const loadArticlesButton = document.getElementById("load-articles-button");
    const categoriesInputField = document.getElementById("categories-input-field");
    const limitInputField = document.getElementById("limit-input-field");
  
    // the rest of the file stays inside here
  


function selectedCategories() {
  return [...grid.querySelectorAll("input:checked")].map((input) => input.value);
}

function setText(root, selector, value) {
  const node = root.querySelector(selector);
  if (node) node.textContent = value || "";
}

function showArticles(articles) {
  container.innerHTML = "";
  if (articles.length === 0) {
    container.innerHTML = "<p>Artikleid ei leitud.</p>";
    return;
  }

  for (const article of articles) {
    const clone = template.content.cloneNode(true);
    setText(clone, ".news-date", article.published);
    setText(clone, ".news-source", article.source);
    setText(clone, ".news-title", article.title);
    const link = clone.querySelector(".news-link");
    if (link && article.link) link.href = article.link;
    container.appendChild(clone);
  }
}

async function loadMatchingArticles() {
    const selected = selectedCategories();
    if (selected.length < 2) return;
  
    //container.innerHTML = "<p>Laen artikleid...</p>";
    const params = new URLSearchParams({
      categories: selected.join(","),
      limit: "5",
    });
    const response = await fetch(`/categorised-feed?${params}`);
    if (!response.ok) throw new Error(`Request failed: ${response.status}`);
    showArticles(await response.json());
  }


loadArticlesButton.addEventListener("click", async () => {
  window.feedPaused = true;
  const selected = selectedCategories();
  if (categoriesInputField.value.trim()) {
    const typed = categoriesInputField.value
      .split(",")
      .map((category) => category.trim())
      .filter(Boolean);
    selected.push(...typed);
  }

  if (selected.length < 2) {
    container.textContent = "Vali vahemalt 2 kategooriat.";
    return;
  }

  const limit = limitInputField.value || "5";
  const params = new URLSearchParams({
    categories: selected.join(","),
    limit,
  });

  container.innerHTML = '<span class="loader"></span>';
  try {
    const response = await fetch(`/categorised-feed?${params}`);
    if (!response.ok) throw new Error(`Request failed: ${response.status}`);
    showArticles(await response.json());
  } catch (error) {
    container.textContent = "Midagi laks valesti, proovi uuesti.";
    console.error(error);
  }
});