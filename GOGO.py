import streamlit as st
import streamlit.components.v1 as components

# 設定網頁標題與寬度
st.set_page_config(page_title="內戰_怪人集結", layout="wide")
st.title("內戰_怪人集結")

game_html = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {
            margin: 0;
            padding: 0;
            display: flex;
            justify-content: center;
            align-items: center;
            background-color: #f0f0f0;
            font-family: 'Arial', sans-serif;
            user-select: none;
        }
        canvas {
            border: 3px solid #2c3e50;
            background: linear-gradient(to bottom, #74b9ff, #fab1a0);
            box-shadow: 0px 8px 20px rgba(0,0,0,0.3);
            border-radius: 4px;
        }
    </style>
</head>
<body>

<canvas id="gameCanvas" width="1000" height="500"></canvas>

<script>
const canvas = document.getElementById('gameCanvas');
const ctx = canvas.getContext('2d');

// 遊戲狀態與參數
let turn = 'dog'; // 'dog' 或 'cat'
let gameOver = false;
let winner = '';

let dogAngle = 45;
let dogPower = 12.0;
let catAngle = 45;
let catPower = 12.0;
let wind = 0; // 負為左，正為右

// 角色位置設定
const dog = { x: 150, y: 410, maxHp: 100, hp: 100 };
const cat = { x: 850, y: 410, maxHp: 100, hp: 100 };
const wall = { x: 485, y: 250, w: 30, h: 250 }; // 中間的紅磚牆

// 砲彈狀態
let projectile = null;
const gravity = 0.25; // 重力加速度

// 初始化隨機風向
changeWind();

// 監聽鍵盤事件來調整角度與力道
window.addEventListener('keydown', (e) => {
    // 阻擋所有遊戲控制按鍵的瀏覽器預設行為（如網頁捲動）
    const gameKeys = [
        'w', 'W', 's', 'S', 'a', 'A', 'd', 'D', ' ', 
        'ArrowUp', 'ArrowDown', 'ArrowLeft', 'ArrowRight', 'Enter'
    ];
    if (gameKeys.includes(e.key) || e.code === 'NumpadEnter') {
        e.preventDefault();
    }

    // 遊戲結束時的重設邏輯
    if (gameOver) {
        if (e.key === ' ' || e.key === 'Enter' || e.code === 'NumpadEnter') {
            resetGame();
        }
        return;
    }

    // 只有在空中沒有砲彈時才可以控制與發射
    if (!projectile) {
        // --- 狗狗回合 (WSAD + 空白鍵) ---
        if (turn === 'dog') {
            // 角度控制：W 增加、S 減少
            if (e.key === 'w' || e.key === 'W') dogAngle = Math.min(90, dogAngle + 1);
            if (e.key === 's' || e.key === 'S') dogAngle = Math.max(0, dogAngle - 1);
            // 力道控制：D 增加、A 減少
            if (e.key === 'd' || e.key === 'D') dogPower = Math.min(30, dogPower + 0.5);
            if (e.key === 'a' || e.key === 'A') dogPower = Math.max(1, dogPower - 0.5);
            // 發射：空白鍵
            if (e.key === ' ') fire(); 
        } 
        // --- 貓咪回合 (方向鍵 + 數字鍵Enter) ---
        else if (turn === 'cat') {
            // 角度控制：上 增加、下 減少
            if (e.key === 'ArrowUp') catAngle = Math.min(90, catAngle + 1);
            if (e.key === 'ArrowDown') catAngle = Math.max(0, catAngle - 1);
            // 力道控制：右 增加、左 減少
            if (e.key === 'ArrowRight') catPower = Math.min(30, catPower + 0.5);
            if (e.key === 'ArrowLeft') catPower = Math.max(1, catPower - 0.5);
            // 發射：必須是數字鍵區的 Enter (NumpadEnter)
            if (e.code === 'NumpadEnter') fire(); 
        }
    }
});

function changeWind() {
    // 隨機風向強度介於 -2.0 到 +2.0 之間
    wind = (Math.random() * 4 - 2);
}

function fire() {
    if (turn === 'dog') {
        projectile = {
            type: 'bone',
            x: dog.x + 25,
            y: dog.y - 15,
            vx: dogPower * Math.cos(dogAngle * Math.PI / 180) * 0.8,
            vy: -dogPower * Math.sin(dogAngle * Math.PI / 180) * 0.8
        };
    } else {
        projectile = {
            type: 'fish',
            x: cat.x - 25,
            y: cat.y - 15,
            // 貓咪面向左邊，所以 X 軸速度要是負的
            vx: -catPower * Math.cos(catAngle * Math.PI / 180) * 0.8,
            vy: -catPower * Math.sin(catAngle * Math.PI / 180) * 0.8
        };
    }
}

function update() {
    if (gameOver) return;

    // 物理模擬：砲彈移動
    if (projectile) {
        // 風向與重力公式計算
        projectile.vx += wind * 0.015; 
        projectile.vy += gravity;
        
        projectile.x += projectile.vx;
        projectile.y += projectile.vy;

        // 1. 碰撞檢測：擊中地面
        if (projectile.y >= 430) {
            endTurn();
        }
        // 2. 碰撞檢測：擊中牆壁
        else if (projectile.x >= wall.x && projectile.x <= wall.x + wall.w &&
                 projectile.y >= wall.y && projectile.y <= 430) {
            endTurn();
        }
        // 3. 碰撞檢測：擊中貓咪 
        else if (turn === 'dog' && Math.hypot(projectile.x - cat.x, projectile.y - cat.y) < 30) {
            cat.hp = Math.max(0, cat.hp - 25); // 每次命中扣 25 滴血
            checkGameOver();
            endTurn();
        }
        // 4. 碰撞檢測：擊中狗狗 
        else if (turn === 'cat' && Math.hypot(projectile.x - dog.x, projectile.y - dog.y) < 30) {
            dog.hp = Math.max(0, dog.hp - 25);
            checkGameOver();
            endTurn();
        }
        // 5. 飛出左右邊界外
        else if (projectile.x < 0 || projectile.x > canvas.width) {
            endTurn();
        }
    }
}

function checkGameOver() {
    if (dog.hp <= 0) {
        gameOver = true;
        winner = '我大獲全勝！';
    } else if (cat.hp <= 0) {
        gameOver = true;
        winner = '你大獲全勝！🐶';
    }
}

function endTurn() {
    projectile = null;
    if (gameOver) return;

    changeWind(); // 換回合時隨機改變風向

    // 切換回合
    if (turn === 'dog') {
        turn = 'cat';
    } else {
        turn = 'dog';
    }
}

function resetGame() {
    dog.hp = 100;
    cat.hp = 100;
    dogAngle = 45;
    dogPower = 12.0;
    catAngle = 45;
    catPower = 12.0;
    gameOver = false;
    winner = '';
    turn = 'dog';
    projectile = null;
    changeWind();
}

function draw() {
    // 清空畫布
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // 1. 繪製背景與地面
    ctx.fillStyle = '#2ebd59'; // 草地綠
    ctx.fillRect(0, 430, canvas.width, 70); 
    ctx.fillStyle = '#fab1a0'; 
    ctx.fillRect(0, 427, canvas.width, 3); 

    // 2. 繪製中間的紅磚牆
    ctx.fillStyle = '#d63031';
    ctx.fillRect(wall.x, wall.y, wall.w, wall.h);
    // 畫磚牆橫線
    ctx.strokeStyle = '#ff7675';
    ctx.lineWidth = 2;
    for(let i = wall.y; i < 430; i+=25) {
        ctx.beginPath(); ctx.moveTo(wall.x, i); ctx.lineTo(wall.x+wall.w, i); ctx.stroke();
    }

        // 3. 繪製犬
    // 身體/頭部主體 (圓形)
    ctx.fillStyle = '#2d3436'; // 深黑灰色
    ctx.beginPath();
    ctx.arc(dog.x, dog.y, 25, 0, Math.PI * 2);
    ctx.fill();

    // 周圍小圓形組合
    ctx.beginPath();
    ctx.arc(dog.x - 15, dog.y - 15, 10, 0, Math.PI * 2); // 左上毛球
    ctx.arc(dog.x + 15, dog.y - 15, 10, 0, Math.PI * 2); // 右上毛球
    ctx.arc(dog.x, dog.y - 20, 12, 0, Math.PI * 2);     // 頭頂大毛球
    ctx.fill();

    // 垂耳 
    ctx.fillRect(dog.x - 28, dog.y - 10, 10, 22); // 左垂耳
    ctx.fillRect(dog.x + 18, dog.y - 10, 10, 22); // 右垂耳

    // 眼睛與鼻子 
    ctx.fillStyle = '#ffffff'; ctx.fillRect(dog.x + 5, dog.y - 8, 5, 5);  // 眼白
    ctx.fillStyle = '#000000'; ctx.fillRect(dog.x + 7, dog.y - 6, 3, 3);  // 瞳孔
    ctx.fillStyle = '#0f1416'; ctx.fillRect(dog.x + 14, dog.y - 2, 6, 5); // 鼻子

    // 舌頭
    ctx.fillStyle = '#ff7675'; 
    ctx.fillRect(dog.x + 12, dog.y + 6, 6, 9); 
    
    // 狗狗血條
    ctx.fillStyle = '#e74c3c'; ctx.fillRect(dog.x - 30, dog.y - 45, 60, 8); // 紅底
    ctx.fillStyle = '#2ecc71'; ctx.fillRect(dog.x - 30, dog.y - 45, 60 * (dog.hp / dog.maxHp), 8); // 綠血


        // 4. 繪製貓
    // 貓咪頭部主體 (圓形)
    ctx.fillStyle = '#e67e22'; // 經典橘貓色
    ctx.beginPath();
    ctx.arc(cat.x, cat.y, 25, 0, Math.PI * 2);
    ctx.fill();

    // 三角形組合
    ctx.beginPath();
    // 左耳三角形
    ctx.moveTo(cat.x - 22, cat.y - 12);
    ctx.lineTo(cat.x - 25, cat.y - 32); // 耳尖
    ctx.lineTo(cat.x - 5, cat.y - 24);
    // 右耳三角形
    ctx.moveTo(cat.x + 22, cat.y - 12);
    ctx.lineTo(cat.x + 25, cat.y - 32); // 耳尖
    ctx.lineTo(cat.x + 5, cat.y - 24);
    ctx.fill();

    // 貓臉特徵
    ctx.fillStyle = '#000000'; 
    ctx.fillRect(cat.x - 14, cat.y - 6, 4, 4); // 左眼 
    ctx.fillRect(cat.x + 2, cat.y - 6, 4, 4);  // 右眼 
    ctx.fillStyle = '#f39c12'; 
    ctx.fillRect(cat.x - 6, cat.y + 2, 4, 3);  // 鼻子 

    // 貓鬍鬚
    ctx.strokeStyle = '#000000'; // 鬍鬚顏色
    ctx.lineWidth = 1.5;         // 鬍鬚粗細
    ctx.beginPath();
    
    // 左邊鬍鬚 
    ctx.moveTo(cat.x - 12, cat.y + 3); ctx.lineTo(cat.x - 32, cat.y + 1);   // 上
    ctx.moveTo(cat.x - 12, cat.y + 5); ctx.lineTo(cat.x - 34, cat.y + 6);   // 中
    ctx.moveTo(cat.x - 12, cat.y + 7); ctx.lineTo(cat.x - 31, cat.y + 11);  // 下
    
    // 右邊鬍鬚
    ctx.moveTo(cat.x + 12, cat.y + 3); ctx.lineTo(cat.x + 32, cat.y + 1);   // 上
    ctx.moveTo(cat.x + 12, cat.y + 5); ctx.lineTo(cat.x + 34, cat.y + 6);   // 中
    ctx.moveTo(cat.x + 12, cat.y + 7); ctx.lineTo(cat.x + 31, cat.y + 11);  // 下
    ctx.stroke();
    // ────────────────────────────

    // 貓貓血條
    ctx.fillStyle = '#e74c3c'; ctx.fillRect(cat.x - 30, cat.y - 45, 60, 8);
    ctx.fillStyle = '#2ecc71'; ctx.fillRect(cat.x - 30, cat.y - 45, 60 * (cat.hp / cat.maxHp), 8);

    // 5. 資訊看板 (狗狗 - 左上)
    ctx.fillStyle = 'rgba(0, 0, 0, 0.7)';
    ctx.fillRect(20, 20, 220, 100);
    ctx.fillStyle = '#fff';
    ctx.font = 'bold 16px Arial';
    ctx.fillText(turn === 'dog' ? '你(換你囉~)' : '你', 35, 45);
    ctx.font = '15px Arial';
    ctx.fillText(`角度: ${dogAngle}°`, 35, 70);
    ctx.fillText(`力道: ${dogPower.toFixed(1)}`, 35, 95);

    // 6. 資訊看板 (貓貓 - 右上)
    ctx.fillStyle = 'rgba(0, 0, 0, 0.7)';
    ctx.fillRect(760, 20, 220, 100);
    ctx.fillStyle = '#fff';
    ctx.font = 'bold 16px Arial';
    ctx.fillText(turn === 'cat' ? '我(換你囉~)' : '我', 775, 45);
    ctx.font = '15px Arial';
    ctx.fillText(`角度: ${catAngle}°`, 775, 70);
    ctx.fillText(`力道: ${catPower.toFixed(1)}`, 775, 95);

    // 7. 上方中央：動態風向標誌
    ctx.fillStyle = 'rgba(44, 62, 80, 0.8)';
    ctx.fillRect(420, 20, 160, 50);
    ctx.fillStyle = '#fff';
    ctx.font = 'bold 16px Arial';
    let windDir = wind >= 0 ? '▶ 右' : '◀ 左';
    ctx.fillText(`風向: ${Math.abs(wind).toFixed(2)} ${windDir}`, 445, 52);

    // 8. 繪製發射武器或預覽線
    if (projectile) {
        ctx.fillStyle = projectile.type === 'bone' ? '#fff' : '#ffeaa7';
        ctx.beginPath();
        // 骨頭/魚條用矩形或圓形簡單示意
        ctx.arc(projectile.x, projectile.y, 7, 0, Math.PI * 2);
        ctx.fill();
    } else if (!gameOver) {
        // 虛線軌跡預覽
        ctx.lineWidth = 2;
        ctx.setLineDash([5, 5]);
        ctx.beginPath();
        
        let tx, ty, tvx, tvy;

        if (turn === 'dog') {
            ctx.strokeStyle = 'rgba(255,255,255,0.5)'; 
            tx = dog.x + 25; 
            ty = dog.y - 15;
            tvx = dogPower * Math.cos(dogAngle * Math.PI / 180) * 0.8;
            tvy = -dogPower * Math.sin(dogAngle * Math.PI / 180) * 0.8;
        } else {
            ctx.strokeStyle = 'rgba(255,255,255,0.5)'; 
            tx = cat.x - 25; 
            ty = cat.y - 15;
            tvx = -catPower * Math.cos(catAngle * Math.PI / 180) * 0.8;
            tvy = -catPower * Math.sin(catAngle * Math.PI / 180) * 0.8;
        }

        ctx.moveTo(tx, ty);
        for(let i=0; i<40; i++) {
            tvx += wind * 0.015; 
            tvy += gravity;
            tx += tvx; 
            ty += tvy;
            ctx.lineTo(tx, ty);
            if (ty > 430 || (tx >= wall.x && tx <= wall.x + wall.w && ty >= wall.y)) break;
        }
        ctx.stroke();
        ctx.setLineDash([]);
    }


    // 9. 遊戲結束畫面覆蓋
    if (gameOver) {
        ctx.fillStyle = 'rgba(0, 0, 0, 0.75)';
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        ctx.fillStyle = '#fff';
        ctx.font = 'bold 40px Arial';
        ctx.textAlign = 'center';
        ctx.fillText(winner, canvas.width / 2, canvas.height / 2 - 20);
        ctx.font = '20px Arial';
        ctx.fillStyle = '#ffeaa7';
        ctx.fillText('點擊畫面 或 按下空白鍵 重新開始遊戲', canvas.width / 2, canvas.height / 2 + 30);
        ctx.textAlign = 'start'; // 恢復對齊設定
    }
}

function gameLoop() {
    update();
    draw();
    window.requestAnimationFrame(gameLoop);
}

// 啟動遊戲
gameLoop();
</script>
F
</body>
</html>
"""

# 在 Streamlit 中渲染 HTML 遊戲畫面
components.html(game_html, height=520, width=1025)

# 提供下方的操作指引說明
st.markdown("""
### 遊戲操作說明
1. 你調整與發射：
   * `W` `S` 鍵調整角度
   * `A` `D` 鍵調整力道
   * 按 `空白鍵`  發射。

2. 我調整與發射：
    * `↑` `↓` 鍵調整角度
    * `←` `→` 鍵調整力道
    * 按 `數字鍵區的 Enter` 發射。
""")
