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


async function loadFeedItems(limit = 5, offset = 0) { // async funktsioon, mis laeb artikleid andmebaasist
  const container = document.getElementById('feed-container'); // valime feed containeri
  const template = document.getElementById('news-template'); // valime news templatei

  try {
    const response = await fetch(`/articles/${limit}/${offset}`); // päring apile, et saada x number artikleid andmebaasist, alates offset-ist
    const articles = await response.json(); // salvestame andmed muutujasse

    container.innerHTML = ''; // eemaldame eelneva feed-containeri sisu

    if (articles.length === 0) { // kui artikleid ei leitud, siis näitame teksti
      container.innerHTML = '<p>Artikleid ei leitud.</p>';
      return;
    }

    articles.forEach(article => { // loopime läbi artiklid
      const clone = template.content.cloneNode(true); // kloonime templatei

      clone.querySelector('.news-date').textContent = article.published;
      clone.querySelector('.news-author').textContent = article.author || '';
      clone.querySelector('.news-title').textContent = article.title;
      clone.querySelector('.news-body').textContent = article.summary;
      clone.querySelector('.news-source').textContent = article.source || '';

      container.appendChild(clone);
    });

  } catch (error) {
    console.error('Error loading news:', error);
    container.innerHTML = '<p>Failed to load news feed.</p>';
  }
}

loadFeedItems();
