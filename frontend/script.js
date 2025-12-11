function syncSlider(inputId, sliderId, valueId, fillId, unit, max) {
    const input = document.getElementById(inputId);
    const slider = document.getElementById(sliderId);
    const value = document.getElementById(valueId);
    const fill = document.getElementById(fillId);

    const update = () => {
        const val = parseFloat(input.value);
        slider.value = val;
        value.textContent = `${val.toFixed(1)} ${unit}`;
        const percent = (val / max) * 100;
        fill.style.width = `${percent}%`;
    };

    input.addEventListener('input', update);
    slider.addEventListener('input', () => {
        input.value = slider.value;
        update();
    });

    update();
}

document.getElementById('photoInput').addEventListener('change', function(e) {
    const file = e.target.files[0];
    const preview = document.getElementById('photoPreview');
    if (file && file.type.startsWith('image/')) {
        const reader = new FileReader();
        reader.onload = function(ev) {
            preview.innerHTML = `<img src="${ev.target.result}" alt="Предпросмотр">`;
        };
        reader.readAsDataURL(file);
    } else {
        preview.innerHTML = '<span>Выберите фото</span>';
    }
});

document.addEventListener('DOMContentLoaded', () => {
    syncSlider('weightInput', 'weightSlider', 'weightValue', 'weightFill', 'кг', 50);
    syncSlider('lengthInput', 'lengthSlider', 'lengthValue', 'lengthFill', 'см', 150);

    const form = document.getElementById('catchForm');
    const message = document.getElementById('message');

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        message.style.display = 'none';
        const formData = new FormData(form);
        try {
            const res = await fetch('/api/catches', {
                method: 'POST',
                body: formData
            });
            if (res.ok) {
                message.textContent = 'Улов успешно сохранён!';
                message.className = 'message success';
                message.style.display = 'block';
                form.reset();
                document.getElementById('photoPreview').innerHTML = '<span>Выберите фото</span>';
                document.getElementById('weightInput').value = 1;
                document.getElementById('lengthInput').value = 30;
                syncSlider('weightInput', 'weightSlider', 'weightValue', 'weightFill', 'кг', 50);
                syncSlider('lengthInput', 'lengthSlider', 'lengthValue', 'lengthFill', 'см', 150);
            } else {
                const err = await res.json();
                message.textContent = err.error || 'Ошибка при сохранении';
                message.className = 'message error';
                message.style.display = 'block';
            }
        } catch (err) {
            message.textContent = 'Ошибка сети';
            message.className = 'message error';
            message.style.display = 'block';
        }
    });
});