const grid = document.getElementById("category-grid");
const output = document.querySelector(".categories-content");

function selectedCategories() {
  return [...grid.querySelectorAll("input:checked")].map((input) => input.value);
}

grid.addEventListener("change", () => {
  const selected = selectedCategories();
  output.textContent = selected.length
    ? selected.join(", ")
    : "No categories selected";
});