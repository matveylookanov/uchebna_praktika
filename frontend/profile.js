document.getElementById('loadCatchesBtn').addEventListener('click', loadCatches);

async function loadCatches() {
    const btn = document.getElementById('loadCatchesBtn');
    const list = document.getElementById('catchesList');
    btn.disabled = true;
    btn.textContent = 'Загрузка...';

    try {
        const res = await fetch('/api/catches');
        const catches = await res.json();
        list.innerHTML = '';

        if (catches.length === 0) {
            list.innerHTML = '<p>У вас пока нет уловов.</p>';
        } else {
            catches.forEach(c => {
                const div = document.createElement('div');
                div.className = 'catch-item';
                const photoHtml = c.photo_path ? `<img src="/${c.photo_path}" alt="Рыба">` : '';
                div.innerHTML = `
                    <div>${photoHtml}</div>
                    <div>
                        <strong>${c.weight_kg} кг, ${c.length_cm} см</strong>
                        <div class="catch-actions">
                            <button onclick="editCatch(${c.id})">Редактировать</button>
                            <button onclick="deleteCatch(${c.id})" style="background:#e74c3c;">Удалить</button>
                        </div>
                    </div>
                `;
                list.appendChild(div);
            });
        }
    } catch (err) {
        list.innerHTML = '<p>Ошибка загрузки уловов.</p>';
    } finally {
        btn.disabled = false;
        btn.textContent = 'Показать мои уловы';
    }
}

async function deleteCatch(id) {
    if (!confirm('Вы уверены, что хотите удалить этот улов?')) return;
    try {
        await fetch(`/api/catches/${id}`, { method: 'DELETE' });
        loadCatches();
    } catch (err) {
        alert('Ошибка удаления');
    }
}

async function editCatch(id) {
    try {
        const res = await fetch(`/api/catches/${id}`);
        const c = await res.json();

        const list = document.getElementById('catchesList');
        list.innerHTML = `
            <div class="catch-item" style="flex-direction: column; gap: 15px;">
                <h3>Редактировать улов #${id}</h3>
                <div class="form-group">
                    <label>Вес (кг):</label>
                    <input type="number" id="editWeight" value="${c.weight_kg}" step="0.1" min="0.1" max="50" required>
                </div>
                <div class="form-group">
                    <label>Длина (см):</label>
                    <input type="number" id="editLength" value="${c.length_cm}" step="1" min="5" max="150" required>
                </div>
                <div class="form-group">
                    <label>Фото:</label>
                    <input type="file" id="editPhoto" accept="image/*">
                </div>
                <div class="catch-actions">
                    <button onclick="saveEdit(${id})">Сохранить</button>
                    <button onclick="cancelEdit()" style="background:#95a5a6;">Отмена</button>
                </div>
            </div>
        `;
    } catch (err) {
        alert('Ошибка загрузки данных для редактирования');
    }
}

async function saveEdit(id) {
    const weight = parseFloat(document.getElementById('editWeight').value);
    const length = parseFloat(document.getElementById('editLength').value);
    const photoInput = document.getElementById('editPhoto');
    const photo = photoInput.files[0];

    if (!weight || !length) {
        alert('Введите вес и длину');
        return;
    }

    const formData = new FormData();
    formData.append('weight_kg', weight);
    formData.append('length_cm', length);
    if (photo) {
        formData.append('photo', photo);
    }

    try {
        const res = await fetch(`/api/catches/${id}`, {
            method: 'PATCH',
            body: formData
        });
        if (res.ok) {
            alert('Улов обновлён!');
            loadCatches();
        } else {
            const err = await res.json();
            alert(err.error || 'Ошибка при обновлении');
        }
    } catch (err) {
        alert('Ошибка сети');
    }
}

function cancelEdit() {
    loadCatches();
}