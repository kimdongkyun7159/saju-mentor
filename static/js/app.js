/* ===== 사주멘토 — 랜딩 페이지 JS ===== */

document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('loginForm');
    const submitBtn = document.getElementById('submitBtn');
    const btnText = submitBtn.querySelector('.btn-text');
    const btnLoader = submitBtn.querySelector('.btn-loader');

    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        // 로딩 상태
        btnText.style.display = 'none';
        btnLoader.style.display = 'inline-flex';
        submitBtn.disabled = true;

        const calendarType = document.querySelector('input[name="calendar_type"]:checked').value;
        const formData = {
            nickname: document.getElementById('nickname').value.trim(),
            birth_year: parseInt(document.getElementById('birthYear').value),
            birth_month: parseInt(document.getElementById('birthMonth').value),
            birth_day: parseInt(document.getElementById('birthDay').value),
            birth_hour: parseInt(document.getElementById('birthHour').value),
            gender: document.getElementById('gender').value,
            calendar_type: calendarType,
            is_intercalation: calendarType === 'lunar' && document.getElementById('isIntercalation').checked,
        };

        try {
            const res = await fetch('/api/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(formData),
            });

            if (!res.ok) {
                const err = await res.json();
                throw new Error(err.detail || '서버 오류');
            }

            const data = await res.json();
            // 채팅 페이지로 이동
            window.location.href = `/chat/${data.user_id}`;
        } catch (err) {
            alert(err.message || '오류가 발생했습니다. 다시 시도해주세요.');
            btnText.style.display = 'inline';
            btnLoader.style.display = 'none';
            submitBtn.disabled = false;
        }
    });

    // 음력 선택 시 윤달 표시
    const calRadios = document.querySelectorAll('input[name="calendar_type"]');
    const intercalWrap = document.getElementById('intercalationWrap');
    calRadios.forEach(r => r.addEventListener('change', () => {
        intercalWrap.style.display = r.value === 'lunar' && r.checked ? 'flex' : 'none';
    }));

    // 파티클 애니메이션 (미니멀)
    createParticles();
});


function createParticles() {
    const container = document.getElementById('particles');
    if (!container) return;

    for (let i = 0; i < 20; i++) {
        const dot = document.createElement('div');
        dot.style.cssText = `
            position: absolute;
            width: ${Math.random() * 3 + 1}px;
            height: ${Math.random() * 3 + 1}px;
            background: rgba(167, 139, 250, ${Math.random() * 0.3 + 0.1});
            border-radius: 50%;
            left: ${Math.random() * 100}%;
            top: ${Math.random() * 100}%;
            animation: particle-drift ${Math.random() * 20 + 15}s linear infinite;
            animation-delay: ${Math.random() * -20}s;
        `;
        container.appendChild(dot);
    }

    // CSS 애니메이션 추가
    if (!document.getElementById('particle-style')) {
        const style = document.createElement('style');
        style.id = 'particle-style';
        style.textContent = `
            @keyframes particle-drift {
                0% { transform: translate(0, 0) scale(1); opacity: 0; }
                10% { opacity: 1; }
                90% { opacity: 1; }
                100% { transform: translate(${Math.random() > 0.5 ? '' : '-'}${Math.random() * 200 + 50}px, -${Math.random() * 300 + 100}px) scale(0.5); opacity: 0; }
            }
        `;
        document.head.appendChild(style);
    }
}
