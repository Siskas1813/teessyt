// Простая реализация Тетриса на канвасе
const canvas = document.getElementById('gameCanvas');
const context = canvas.getContext('2d');
const blockSize = 30;
canvas.width = blockSize * 10;
canvas.height = blockSize * 20;

const colors = {
    I: '#00bcd4',
    J: '#3f51b5',
    L: '#ff9800',
    O: '#ffeb3b',
    S: '#4caf50',
    T: '#9c27b0',
    Z: '#f44336'
};

const shapes = {
    I: [[1, 1, 1, 1]],
    J: [
        [1, 0, 0],
        [1, 1, 1]
    ],
    L: [
        [0, 0, 1],
        [1, 1, 1]
    ],
    O: [
        [1, 1],
        [1, 1]
    ],
    S: [
        [0, 1, 1],
        [1, 1, 0]
    ],
    T: [
        [0, 1, 0],
        [1, 1, 1]
    ],
    Z: [
        [1, 1, 0],
        [0, 1, 1]
    ]
};

function drawMatrix(matrix, offset, color) {
    context.fillStyle = color;
    matrix.forEach((row, y) => {
        row.forEach((value, x) => {
            if (value) {
                context.fillRect((x + offset.x) * blockSize,
                                 (y + offset.y) * blockSize,
                                 blockSize, blockSize);
            }
        });
    });
}

function createPiece(type) {
    return shapes[type];
}

function merge(arena, piece) {
    piece.matrix.forEach((row, y) => {
        row.forEach((value, x) => {
            if (value) {
                arena[y + piece.pos.y][x + piece.pos.x] = value;
            }
        });
    });
}

function collide(arena, piece) {
    for (let y = 0; y < piece.matrix.length; ++y) {
        for (let x = 0; x < piece.matrix[y].length; ++x) {
            if (piece.matrix[y][x] !== 0 &&
                (arena[y + piece.pos.y] &&
                 arena[y + piece.pos.y][x + piece.pos.x]) !== 0) {
                return true;
            }
        }
    }
    return false;
}

function rotate(matrix) {
    for (let y = 0; y < matrix.length; ++y) {
        for (let x = 0; x < y; ++x) {
            [matrix[x][y], matrix[y][x]] = [matrix[y][x], matrix[x][y]];
        }
    }
    matrix.forEach(row => row.reverse());
}

function createArena(w, h) {
    const arena = [];
    while (h--) {
        arena.push(new Array(w).fill(0));
    }
    return arena;
}

const arena = createArena(10, 20);

let dropCounter = 0;
let dropInterval = 1000;
let lastTime = 0;

function playerDrop() {
    player.pos.y++;
    if (collide(arena, player)) {
        player.pos.y--;
        merge(arena, player);
        resetPlayer();
        arenaSweep();
    }
    dropCounter = 0;
}

function playerMove(dir) {
    player.pos.x += dir;
    if (collide(arena, player)) {
        player.pos.x -= dir;
    }
}

function playerRotate() {
    const pos = player.pos.x;
    rotate(player.matrix);
    let offset = 1;
    while (collide(arena, player)) {
        player.pos.x += offset;
        offset = -(offset + (offset > 0 ? 1 : -1));
        if (offset > player.matrix[0].length) {
            rotate(player.matrix);
            player.pos.x = pos;
            return;
        }
    }
}

function arenaSweep() {
    outer: for (let y = arena.length - 1; y >= 0; --y) {
        for (let x = 0; x < arena[y].length; ++x) {
            if (arena[y][x] === 0) {
                continue outer;
            }
        }
        const row = arena.splice(y, 1)[0].fill(0);
        arena.unshift(row);
        ++y;
    }
}

function draw() {
    context.fillStyle = '#fdfdfd';
    context.fillRect(0, 0, canvas.width, canvas.height);

    drawMatrix(arena, {x: 0, y: 0}, '#cccccc');
    drawMatrix(player.matrix, player.pos, colors[player.type]);
}

function update(time = 0) {
    const deltaTime = time - lastTime;
    lastTime = time;

    dropCounter += deltaTime;
    if (dropCounter > dropInterval) {
        playerDrop();
    }

    draw();
    requestAnimationFrame(update);
}

document.addEventListener('keydown', event => {
    if (event.key === 'ArrowLeft') {
        playerMove(-1);
    } else if (event.key === 'ArrowRight') {
        playerMove(1);
    } else if (event.key === 'ArrowDown') {
        playerDrop();
    } else if (event.key === 'ArrowUp') {
        playerRotate();
    }
});

function resetPlayer() {
    const pieces = 'TJLOSZI';
    player.type = pieces[pieces.length * Math.random() | 0];
    player.matrix = createPiece(player.type);
    player.pos.y = 0;
    player.pos.x = (arena[0].length / 2 | 0) -
                   (player.matrix[0].length / 2 | 0);
    if (collide(arena, player)) {
        arena.forEach(row => row.fill(0));
    }
}

const player = {
    pos: {x: 0, y: 0},
    matrix: null,
    type: 'I'
};

resetPlayer();
update();
