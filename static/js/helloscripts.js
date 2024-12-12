function search(directions) {
    const query = document.querySelector('.search-box input').value.trim().toLowerCase();
    const resultsList = document.getElementById('results-list');
    const resultsContainer = document.getElementById('search-results');
    resultsList.innerHTML = "";
    if (query !== "") {
        const filteredDirections = directions.filter(dir =>
            dir.name.toLowerCase().includes(query) || dir.code.includes(query)
        );
        if (filteredDirections.length > 0) {
            filteredDirections.forEach(dir => {
                const li = document.createElement('li');
                li.innerHTML = `
                    <strong>${dir.name}</strong> ${dir.code}<br>
                    <div>
                        <span>Популярность: ${dir.popularity}</span>
                        <span>Мин. средний балл: ${dir.min_avg_score}</span>
                        <span>Стоимость: ${dir.cost} руб.</span>
                        <span>Бюджетных мест: ${dir.budget_places}</span>
                    </div>
                `;
                resultsList.appendChild(li);
            });
        } else {
            const li = document.createElement('li');
            li.textContent = 'Ничего не найдено';
            resultsList.appendChild(li);
        }
        resultsContainer.style.display = 'block';
    } else {
        alert('Пожалуйста, введите запрос для поиска!');
    }
}
function goToPage(url) {
    window.location.href = url;
}