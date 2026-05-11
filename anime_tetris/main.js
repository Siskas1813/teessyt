const SIZE = 5;
const TARGET = 4;

const boardEl = document.getElementById('board');
const hudEl = document.getElementById('hud');
const logEl = document.getElementById('log');
const buttons = [...document.querySelectorAll('button[data-action]')];

const state = {
  turn: 'X',
  action: 'place',
  mana: { X: 1, O: 1 },
  energy: { X: 0, O: 0 },
  winner: null,
  selected: null,
  board: Array.from({ length: SIZE * SIZE }, () => ({
    owner: null,
    shield: 0,
    frozen: 0,
    cursed: 0,
    blocked: 0,
    type: 'normal'
  }))
};

function idx(r, c) { return r * SIZE + c; }
function rc(i) { return [Math.floor(i / SIZE), i % SIZE]; }
function enemyOf(p) { return p === 'X' ? 'O' : 'X'; }
function log(msg) { logEl.innerHTML = `<div>• ${msg}</div>` + logEl.innerHTML; }

function setupSpecialCells() {
  state.board[idx(0, 0)].type = 'mana';
  state.board[idx(4, 4)].type = 'mana';
  state.board[idx(0, 4)].type = 'sanctuary';
  state.board[idx(4, 0)].type = 'sanctuary';
  state.board[idx(1, 1)].type = 'portal';
  state.board[idx(3, 3)].type = 'portal';
  state.board[idx(2, 4)].type = 'cursed';
}

function cost(action) {
  return { place: 0, shield: 1, freeze: 2, burn: 2, dash: 2, assassinate: 3, ultimate: 0, end: 0 }[action] ?? 0;
}

function canAfford(action) {
  if (action === 'ultimate') return state.energy[state.turn] >= 7;
  return state.mana[state.turn] >= cost(action);
}

function consume(action) {
  if (action === 'ultimate') state.energy[state.turn] -= 7;
  else state.mana[state.turn] -= cost(action);
}

function neighbors(i) {
  const [r, c] = rc(i);
  const out = [];
  [[1,0],[-1,0],[0,1],[0,-1],[1,1],[1,-1],[-1,1],[-1,-1]].forEach(([dr, dc]) => {
    const nr = r + dr; const nc = c + dc;
    if (nr >= 0 && nr < SIZE && nc >= 0 && nc < SIZE) out.push(idx(nr, nc));
  });
  return out;
}

function place(i) {
  const cell = state.board[i];
  if (cell.owner || cell.blocked > 0) return false;
  cell.owner = state.turn;
  if (cell.type === 'cursed') cell.cursed = 2;
  if (cell.type === 'mana') state.mana[state.turn] += 1;
  return true;
}

function winCheck(player) {
  const dirs = [[0,1],[1,0],[1,1],[1,-1]];
  for (let r = 0; r < SIZE; r++) {
    for (let c = 0; c < SIZE; c++) {
      for (const [dr, dc] of dirs) {
        let ok = true;
        for (let k = 0; k < TARGET; k++) {
          const nr = r + dr * k, nc = c + dc * k;
          if (nr < 0 || nr >= SIZE || nc < 0 || nc >= SIZE) { ok = false; break; }
          const cell = state.board[idx(nr, nc)];
          if (cell.owner !== player || cell.cursed > 0) { ok = false; break; }
        }
        if (ok) return true;
      }
    }
  }
  return false;
}

function endTurn() {
  state.board.forEach(cell => {
    cell.frozen = Math.max(0, cell.frozen - 1);
    cell.blocked = Math.max(0, cell.blocked - 1);
    cell.cursed = Math.max(0, cell.cursed - 1);
  });
  const foe = enemyOf(state.turn);
  state.turn = foe;
  state.mana[state.turn] += 1;
  state.action = 'place';
  state.selected = null;
  render();
}

function applyAction(i) {
  if (state.winner || !canAfford(state.action)) return;
  const me = state.turn;
  const foe = enemyOf(me);
  const cell = state.board[i];

  if (state.action === 'place') {
    if (!place(i)) return;
    consume('place');
    log(`${me} поставил знак.`);
  } else if (state.action === 'shield') {
    if (cell.owner !== me) return;
    cell.shield = 1;
    consume('shield');
    log(`${me} активировал щит.`);
  } else if (state.action === 'freeze') {
    if (cell.owner !== foe) return;
    cell.frozen = 1;
    consume('freeze');
    log(`${me} заморозил вражеский знак.`);
  } else if (state.action === 'burn') {
    if (cell.owner) return;
    cell.blocked = 1;
    consume('burn');
    log(`${me} сжёг клетку на 1 ход.`);
  } else if (state.action === 'assassinate') {
    if (cell.owner !== foe) return;
    const nearAlly = neighbors(i).some(n => state.board[n].owner === foe);
    if (nearAlly || cell.type === 'sanctuary') return;
    if (cell.shield) { cell.shield = 0; }
    else cell.owner = null;
    consume('assassinate');
    state.energy[me] += 2;
    log(`${me} применил убийство.`);
  } else if (state.action === 'dash') {
    if (state.selected == null) {
      if (cell.owner !== me) return;
      state.selected = i;
      render();
      return;
    }
    const from = state.selected;
    const fromCell = state.board[from];
    if (cell.owner || cell.blocked > 0 || !neighbors(from).includes(i)) return;
    cell.owner = me;
    cell.shield = fromCell.shield;
    fromCell.owner = null; fromCell.shield = 0;
    state.selected = null;
    consume('dash');
    log(`${me} выполнил рывок.`);
  } else if (state.action === 'ultimate') {
    const affected = [i, ...neighbors(i).slice(0, 2)];
    affected.forEach(a => {
      if (state.board[a].owner === foe) state.board[a].owner = null;
    });
    consume('ultimate');
    log(`${me} применил ульту: Метеоритный дождь.`);
  }

  if (winCheck(me)) {
    state.winner = me;
    log(`Победа ${me}!`);
  } else {
    state.energy[me] += 1;
    endTurn();
  }
  render();
}

function render() {
  hudEl.innerHTML = `
    <strong>Ход: ${state.turn}</strong><br>
    Мана X/O: ${state.mana.X} / ${state.mana.O} · Энергия X/O: ${state.energy.X} / ${state.energy.O}
    ${state.winner ? `<br><strong>Победитель: ${state.winner}</strong>` : ''}
  `;

  buttons.forEach(btn => {
    const action = btn.dataset.action;
    btn.classList.toggle('active', action === state.action);
    if (action === 'end') return;
    btn.disabled = state.winner ? true : !canAfford(action) && action !== 'place';
  });

  boardEl.innerHTML = '';
  state.board.forEach((cell, i) => {
    const div = document.createElement('button');
    div.className = `cell ${cell.type} ${cell.blocked ? 'blocked' : ''} ${state.selected === i ? 'selected' : ''}`;
    const markClass = cell.owner === 'X' ? 'mark-x' : 'mark-o';
    const freeze = cell.frozen ? '❄️' : '';
    const shield = cell.shield ? '🛡️' : '';
    const curse = cell.cursed ? '☠️' : '';
    div.innerHTML = `<span class="${markClass}">${cell.owner ?? '·'}</span><small>${freeze}${shield}${curse}</small>`;
    div.onclick = () => applyAction(i);
    boardEl.appendChild(div);
  });
}

buttons.forEach(btn => {
  btn.addEventListener('click', () => {
    if (btn.dataset.action === 'end') return endTurn();
    state.action = btn.dataset.action;
    state.selected = null;
    render();
  });
});

setupSpecialCells();
log('Матч начался. Соберите 4 в ряд на поле 5×5.');
render();
