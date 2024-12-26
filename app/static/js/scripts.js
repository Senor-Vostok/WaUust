function toggleCard(card) {
    const isExpanded = card.classList.contains('expanded');
    document.querySelectorAll('.card').forEach(c => {
        c.classList.remove('expanded');
        c.querySelector('.card-description').innerHTML = '';
    });
    if (!isExpanded) {
        card.classList.add('expanded');
        const description = card.getAttribute('data-description');
        card.querySelector('.card-description').innerHTML = description;
        const cardColor = window.getComputedStyle(card).backgroundColor;
        const darkerColor = darkenColor(cardColor, 0.7);
        document.body.style.backgroundColor = darkerColor;
        const scaleValues = document.querySelectorAll('.scale-values');
        scaleValues.forEach(element => {
            element.style.color = '#ffffff';
        });
    } else {
        document.body.style.backgroundColor = '#d9dcde';
        const scaleValues = document.querySelectorAll('.scale-values');
        scaleValues.forEach(element => {
            element.style.color = '#333';
        });
    }
}
function darkenColor(rgb, factor) {
    const match = rgb.match(/^rgb\((\d+),\s*(\d+),\s*(\d+)\)$/);
    if (!match) return rgb;
    const [_, r, g, b] = match.map(Number);
    const darken = value => Math.max(0, Math.floor(value * factor));
    return `rgb(${darken(r)}, ${darken(g)}, ${darken(b)})`;
}
function applyGradientToCards() {
    const cards = document.querySelectorAll('.card');
    const totalCards = cards.length;
    cards.forEach((card, index) => {
        const greenValue = Math.floor((255 - (index / totalCards) * 255) * 0.85);
        const redValue = Math.floor(((index / totalCards) * 255) * 0.85);
        const blueValue = Math.floor(200 - (index / totalCards) * 100);
        card.style.backgroundColor = `rgb(${redValue}, ${greenValue}, ${blueValue})`;
    });
}
document.getElementById('search-button').addEventListener('click', function() {
    const query = document.getElementById('search-input').value.toLowerCase();
    const cards = document.querySelectorAll('.card');
    cards.forEach(card => {
        const title = card.querySelector('.card-title').textContent.toLowerCase();
        card.style.display = title.includes(query) ? 'block' : 'none';
    });
});
document.getElementById('search-input').addEventListener('input', function() {
    const query = this.value.toLowerCase();
    const cards = document.querySelectorAll('.card');
    cards.forEach(card => {
        const title = card.querySelector('.card-title').textContent.toLowerCase();
        card.style.display = title.includes(query) ? 'block' : 'none';
    });
});
function updateScrollIndicator() {
    const indicator = document.getElementById('scroll-indicator');
    const scrollTop = window.scrollY;
    const docHeight = document.documentElement.scrollHeight;
    const windowHeight = window.innerHeight;
    const scrollPercentage = scrollTop / (docHeight - windowHeight);
    const indicatorHeight = document.querySelector('.scale-gradient').clientHeight;
    indicator.style.top = `${scrollPercentage * (indicatorHeight - indicator.clientHeight)}px`;
}
document.getElementById('apply-filters').addEventListener('click', function () {
    const category = document.getElementById('filter-category').value;
    const sortOption = document.querySelector('input[name="sort"]:checked').value;
    const form = document.createElement('form');
    form.method = 'POST';
    form.action = '/update-data';
    const categoryInput = document.createElement('input');
    categoryInput.type = 'hidden';
    categoryInput.name = 'category';
    categoryInput.value = category;
    form.appendChild(categoryInput);
    const sortInput = document.createElement('input');
    sortInput.type = 'hidden';
    sortInput.name = 'sort';
    sortInput.value = sortOption;
    form.appendChild(sortInput);
    document.body.appendChild(form);
    form.submit();
});
document.addEventListener('scroll', updateScrollIndicator);
document.addEventListener('DOMContentLoaded', applyGradientToCards);