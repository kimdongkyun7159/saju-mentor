/* ===== 사주멘토 — 채팅 JS ===== */

(function init() {
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
        return;
    }
    const messagesEl = document.getElementById('chatMessages');
    const chatForm = document.getElementById('chatForm');
    const chatInput = document.getElementById('chatInput');
    const sendBtn = document.getElementById('sendBtn');
    const quickActions = document.getElementById('quickActions');
    const sidebar = document.getElementById('sidebar');
    const mobileMenu = document.getElementById('mobileMenu');
    const newChatBtn = document.getElementById('newChatBtn');

    // 사주 그리드 렌더링
    renderSajuGrid(SAJU_DATA);
    renderOhengBars(SAJU_DATA);
    renderSajuSummary(SAJU_DATA);
    renderCurrentFortune(SAJU_DATA);
    renderDaeunFlow(SAJU_DATA);

    // 인사 메시지 표시
    addMessage('assistant', GREETING);

    // 메시지 전송
    chatForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const msg = chatInput.value.trim();
        if (!msg) return;
        await sendMessage(msg);
    });

    // 빠른 질문 칩
    quickActions.addEventListener('click', async (e) => {
        const chip = e.target.closest('.chip');
        if (!chip) return;
        const category = chip.dataset.category;
        const labels = {
            personality: '내 성격과 기질을 자세히 분석해주세요',
            career: '직업과 적성을 알려주세요',
            love: '연애운과 배우자상을 봐주세요',
            wealth: '재물운을 자세히 봐주세요',
            health: '건강운은 어떤가요?',
            fortune: '올해 운세를 분야별로 자세히 풀어주세요',
            monthly: '올해 12개월 월별 운세를 알려주세요',
            supplement: '부족한 오행 보충법과 행운 아이템을 알려주세요',
        };
        await sendMessage(labels[category] || category);
    });

    // 모바일 사이드바
    mobileMenu?.addEventListener('click', () => toggleSidebar());
    newChatBtn?.addEventListener('click', () => {
        window.location.href = '/';
    });

    async function sendMessage(text) {
        addMessage('user', text);
        chatInput.value = '';
        sendBtn.disabled = true;

        // 타이핑 인디케이터
        const typingEl = showTyping();

        try {
            const res = await fetch('/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ user_id: USER_ID, message: text }),
            });

            typingEl.remove();

            if (!res.ok) throw new Error('서버 오류');

            const data = await res.json();
            addMessage('assistant', data.response);
        } catch (err) {
            typingEl.remove();
            addMessage('assistant', '죄송합니다, 일시적인 오류가 발생했어요. 다시 시도해주세요.');
        } finally {
            sendBtn.disabled = false;
            chatInput.focus();
        }
    }

    function addMessage(role, text) {
        const div = document.createElement('div');
        div.className = `message ${role}`;
        div.innerHTML = parseMarkdown(text);
        messagesEl.appendChild(div);
        messagesEl.scrollTop = messagesEl.scrollHeight;
    }

    function showTyping() {
        const div = document.createElement('div');
        div.className = 'typing-indicator';
        div.innerHTML = '<div class="typing-dot"></div><div class="typing-dot"></div><div class="typing-dot"></div>';
        messagesEl.appendChild(div);
        messagesEl.scrollTop = messagesEl.scrollHeight;
        return div;
    }

    function parseMarkdown(text) {
        return text
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
            .replace(/={10,}/g, '<hr class="section-divider">')
            .replace(/---/g, '<hr class="light-divider">')
            .replace(/^(★+)(☆*)/gm, (m, filled, empty) => {
                return `<span class="stars">${filled}${empty}</span>`;
            })
            .replace(/\n/g, '<br>');
    }

    function toggleSidebar() {
        sidebar.classList.toggle('open');
        let overlay = document.querySelector('.sidebar-overlay');
        if (!overlay) {
            overlay = document.createElement('div');
            overlay.className = 'sidebar-overlay';
            overlay.addEventListener('click', () => toggleSidebar());
            document.body.appendChild(overlay);
        }
        overlay.classList.toggle('active');
    }
})();

// 오행 색상 맵
const OHENG_COLORS = { '목': '#4ade80', '화': '#f87171', '토': '#fbbf24', '금': '#e2e8f0', '수': '#60a5fa' };

function renderSajuGrid(data) {
    const grid = document.getElementById('sajuGrid');
    if (!grid || !data?.pillars) return;

    const positions = [
        { key: 'hour', label: '시주' },
        { key: 'day', label: '일주' },
        { key: 'month', label: '월주' },
        { key: 'year', label: '년주' },
    ];

    const OHENG_MAP = {
        '갑': '목', '을': '목', '병': '화', '정': '화', '무': '토',
        '기': '토', '경': '금', '신': '금', '임': '수', '계': '수',
        '인': '목', '묘': '목', '사': '화', '오': '화',
        '진': '토', '술': '토', '축': '토', '미': '토',
        '신': '금', '유': '금', '해': '수', '자': '수',
    };

    grid.innerHTML = positions.map(pos => {
        const p = data.pillars[pos.key];
        const stemOheng = OHENG_MAP[p.stem] || '';
        const branchOheng = OHENG_MAP[p.branch] || '';
        const sipsung = data.sipsung?.[pos.key]?.stem_sipsung || '';
        return `
            <div class="saju-pillar">
                <div class="pillar-label">${pos.label}</div>
                <div class="pillar-stem oheng-${stemOheng}">${p.stem}</div>
                <div class="pillar-branch oheng-${branchOheng}">${p.branch}</div>
                <div class="pillar-sipsung">${sipsung}</div>
            </div>
        `;
    }).join('');
}

function renderOhengBars(data) {
    const el = document.getElementById('ohengBars');
    if (!el || !data?.oheng_balance) return;

    const EMOJI = { '목': '🌿', '화': '🔥', '토': '🏔️', '금': '⚙️', '수': '💧' };
    const COLORS = { '목': '#4ade80', '화': '#f87171', '토': '#fbbf24', '금': '#cbd5e1', '수': '#60a5fa' };
    const maxCount = 8;

    let html = '<h4 class="section-title">오행 비율</h4><div class="oheng-bar-list">';
    for (const elem of ['목', '화', '토', '금', '수']) {
        const info = data.oheng_balance[elem] || {};
        const count = info.count || 0;
        const pct = Math.round((count / maxCount) * 100);
        html += `
            <div class="oheng-bar-row">
                <span class="ob-label">${EMOJI[elem]} ${elem}</span>
                <div class="ob-track">
                    <div class="ob-fill" style="width:${pct}%; background:${COLORS[elem]}"></div>
                </div>
                <span class="ob-count">${count}개</span>
                <span class="ob-status">${info.status || ''}</span>
            </div>
        `;
    }
    html += '</div>';
    el.innerHTML = html;
}

function renderSajuSummary(data) {
    const el = document.getElementById('sajuSummary');
    if (!el || !data) return;

    const items = [
        { label: '일간', value: data.summary?.ilgan_desc || '' },
        { label: '강약', value: data.summary?.strength || '' },
        { label: '격국', value: data.summary?.geokguk || '' },
        { label: '용신', value: data.yongsin?.yongsin || '' },
    ];

    const sinsal = (data.sinsal || []).map(s => s.name).join(', ');
    if (sinsal) items.push({ label: '신살', value: sinsal });

    el.innerHTML = items.map(item =>
        `<div class="summary-item">
            <span class="summary-label">${item.label}</span>
            <span class="summary-value">${item.value}</span>
        </div>`
    ).join('');

    const sajuEl = document.getElementById('userSaju');
    if (sajuEl && data.summary?.saju) {
        sajuEl.textContent = data.summary.saju;
    }
}

function renderCurrentFortune(data) {
    const el = document.getElementById('currentFortune');
    if (!el || !data) return;

    const cd = data.current_daeun || {};
    const yf = data.yearly_fortune || {};
    const mf = data.monthly_fortune || {};

    const ohengClass = (oheng) => oheng ? `oheng-${oheng}` : '';

    el.innerHTML = `
        <h4 class="section-title">현재 운세</h4>
        <div class="fortune-cards">
            <div class="fortune-card">
                <span class="fc-label">대운(10년)</span>
                <span class="fc-value ${ohengClass(cd.oheng)}">${cd.pillar || '-'}</span>
                <span class="fc-sipsung">${cd.stem_sipsung || '-'}</span>
            </div>
            <div class="fortune-card highlight">
                <span class="fc-label">${yf.year || ''}년 세운</span>
                <span class="fc-value ${ohengClass(yf.oheng)}">${yf.pillar || '-'}</span>
                <span class="fc-sipsung">${yf.stem_sipsung || '-'}</span>
            </div>
            <div class="fortune-card">
                <span class="fc-label">${mf.month || ''}월 월운</span>
                <span class="fc-value ${ohengClass(mf.oheng)}">${mf.pillar || '-'}</span>
                <span class="fc-sipsung">${mf.stem_sipsung || '-'}</span>
            </div>
        </div>
    `;
}

function renderDaeunFlow(data) {
    const el = document.getElementById('daeunFlow');
    if (!el || !data.daeun?.daeun_list) return;

    const currentAge = data.current_daeun?.start_age;
    const list = data.daeun.daeun_list;

    let html = '<h4 class="section-title">대운 흐름</h4><div class="daeun-timeline">';

    list.forEach(d => {
        const isCurrent = d.start_age === currentAge ? 'current' : '';
        const ohengClass = d.oheng ? `oheng-${d.oheng}` : '';
        html += `
            <div class="daeun-item ${isCurrent}">
                <div class="di-age">${d.start_age}~${d.end_age}세</div>
                <div class="di-pillar ${ohengClass}">${d.pillar}</div>
                <div class="di-sipsung">${d.stem_sipsung}</div>
            </div>
        `;
    });

    html += '</div>';
    el.innerHTML = html;
}
