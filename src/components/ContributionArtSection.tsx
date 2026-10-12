import React, { useState, useEffect, useRef } from 'react';
import { Play, Pause, RotateCcw, ChevronDown, ChevronRight, Gamepad2, Sparkles, Box } from 'lucide-react';

interface ContributionArtSectionProps {
  isLightMode: boolean;
}

export const ContributionArtSection: React.FC<ContributionArtSectionProps> = ({ isLightMode }) => {
  const [pacmanOpen, setPacmanOpen] = useState(true);
  const [isometricOpen, setIsometricOpen] = useState(false);
  const [isSnakePlaying, setIsSnakePlaying] = useState(true);
  const [isPacmanPlaying, setIsPacmanPlaying] = useState(true);
  const [snakeProgress, setSnakeProgress] = useState(35);

  // Canvas Refs
  const snakeCanvasRef = useRef<HTMLCanvasElement | null>(null);
  const pacmanCanvasRef = useRef<HTMLCanvasElement | null>(null);
  const isoCanvasRef = useRef<HTMLCanvasElement | null>(null);

  // Month labels for 52-week calendar
  const months = ['Oct', 'Nov', 'Dec', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct'];

  // ----------------------------------------------------
  // 1. LIVE SNAKE ANIMATION ON CONTRIBUTION GRID
  // ----------------------------------------------------
  useEffect(() => {
    const canvas = snakeCanvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const cols = 52;
    const rows = 7;
    const cellSize = 13;
    const gap = 3;
    canvas.width = cols * (cellSize + gap);
    canvas.height = rows * (cellSize + gap);

    // Initial contribution grid seed based on real activity
    const grid: number[][] = Array.from({ length: cols }, (_, c) =>
      Array.from({ length: rows }, (_, r) => {
        // Higher activity in recent months (columns 40-52)
        if (c > 42 && (r === 2 || r === 3 || r === 4 || r === 5)) return Math.floor(Math.random() * 3) + 2;
        if (c > 35 && Math.random() > 0.6) return Math.floor(Math.random() * 3) + 1;
        if (Math.random() > 0.88) return 1;
        return 0;
      })
    );

    // Snake state
    let snake = [
      { x: 38, y: 3 },
      { x: 37, y: 3 },
      { x: 36, y: 3 },
      { x: 35, y: 3 },
      { x: 35, y: 4 },
      { x: 35, y: 5 },
    ];
    let dir = { x: 1, y: 0 };
    let food = { x: 44, y: 2 };
    let animationId: number;
    let lastTime = 0;
    const moveInterval = 120; // 120ms per step
    let progress = 30;

    const spawnFood = () => {
      food = {
        x: Math.floor(Math.random() * cols),
        y: Math.floor(Math.random() * rows),
      };
    };

    const draw = (time: number) => {
      if (isSnakePlaying && time - lastTime > moveInterval) {
        lastTime = time;

        // Smart steering towards food or roving
        const head = snake[0];
        const dx = food.x - head.x;
        const dy = food.y - head.y;

        if (Math.random() > 0.25) {
          if (Math.abs(dx) > Math.abs(dy)) {
            dir = { x: dx > 0 ? 1 : -1, y: 0 };
          } else if (dy !== 0) {
            dir = { x: 0, y: dy > 0 ? 1 : -1 };
          }
        } else {
          // occasional turn
          const dirs = [
            { x: 1, y: 0 },
            { x: -1, y: 0 },
            { x: 0, y: 1 },
            { x: 0, y: -1 },
          ];
          dir = dirs[Math.floor(Math.random() * dirs.length)];
        }

        const newHead = {
          x: (head.x + dir.x + cols) % cols,
          y: (head.y + dir.y + rows) % rows,
        };

        snake.unshift(newHead);

        if (newHead.x === food.x && newHead.y === food.y) {
          grid[food.x][food.y] = Math.min(grid[food.x][food.y] + 1, 4);
          spawnFood();
        } else {
          snake.pop();
        }

        progress = (progress + 0.3) % 100;
        setSnakeProgress(Math.floor(progress));
      }

      // Render
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      // 1. Draw Grid Cells
      for (let c = 0; c < cols; c++) {
        for (let r = 0; r < rows; r++) {
          const val = grid[c][r];
          const x = c * (cellSize + gap);
          const y = r * (cellSize + gap);

          let fill = isLightMode ? '#E2F0EA' : '#101B1D';
          if (val === 1) fill = isLightMode ? '#A3D9C5' : '#143831';
          if (val === 2) fill = isLightMode ? '#55C29C' : '#1B5448';
          if (val === 3) fill = isLightMode ? '#1C936E' : '#237865';
          if (val >= 4) fill = isLightMode ? '#0D604B' : '#47B68D';

          ctx.fillStyle = fill;
          ctx.beginPath();
          ctx.roundRect(x, y, cellSize, cellSize, 2.5);
          ctx.fill();
        }
      }

      // 2. Draw Food Pellet (glowing commit)
      const fx = food.x * (cellSize + gap);
      const fy = food.y * (cellSize + gap);
      ctx.fillStyle = isLightMode ? '#0D604B' : '#00E5A3';
      ctx.shadowColor = isLightMode ? '#0D604B' : '#00E5A3';
      ctx.shadowBlur = 8;
      ctx.beginPath();
      ctx.roundRect(fx, fy, cellSize, cellSize, 3);
      ctx.fill();
      ctx.shadowBlur = 0;

      // 3. Draw Snake
      snake.forEach((segment, idx) => {
        const sx = segment.x * (cellSize + gap);
        const sy = segment.y * (cellSize + gap);
        const isHead = idx === 0;

        ctx.fillStyle = isHead
          ? isLightMode ? '#065F46' : '#8DE0C1'
          : isLightMode ? '#0D604B' : '#47B68D';

        ctx.beginPath();
        ctx.roundRect(sx, sy, cellSize, cellSize, isHead ? 4 : 2);
        ctx.fill();

        // Snake eyes on head
        if (isHead) {
          ctx.fillStyle = isLightMode ? '#FFFFFF' : '#080D0F';
          ctx.beginPath();
          ctx.arc(sx + 4, sy + 4, 1.5, 0, Math.PI * 2);
          ctx.arc(sx + 9, sy + 4, 1.5, 0, Math.PI * 2);
          ctx.fill();
        }
      });

      animationId = requestAnimationFrame(draw);
    };

    animationId = requestAnimationFrame(draw);
    return () => cancelAnimationFrame(animationId);
  }, [isLightMode, isSnakePlaying]);

  // ----------------------------------------------------
  // 2. LIVE PAC-MAN ANIMATION OVER CONTRIBUTION GRAPH
  // ----------------------------------------------------
  useEffect(() => {
    if (!pacmanOpen) return;
    const canvas = pacmanCanvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const cols = 52;
    const rows = 7;
    const cellSize = 13;
    const gap = 3;
    canvas.width = cols * (cellSize + gap);
    canvas.height = rows * (cellSize + gap);

    // Pac-Man Maze Paths definition (corridors matching Screenshot 192305.png)
    const mazeWalls = [
      // Left section
      { x1: 0, y1: 2, x2: 4, y2: 2 },
      { x1: 2, y1: 2, x2: 2, y2: 6 },
      { x1: 0, y1: 6, x2: 4, y2: 6 },
      { x1: 6, y1: 1, x2: 6, y2: 5 },
      { x1: 6, y1: 2, x2: 12, y2: 2 },
      { x1: 8, y1: 2, x2: 8, y2: 6 },
      { x1: 8, y1: 6, x2: 13, y2: 6 },
      // Middle left
      { x1: 14, y1: 6, x2: 17, y2: 6 },
      { x1: 14, y1: 2, x2: 20, y2: 2 },
      { x1: 17, y1: 2, x2: 17, y2: 6 },
      { x1: 20, y1: 3, x2: 20, y2: 6 },
      // Ghost pen at center
      { x1: 24, y1: 3, x2: 28, y2: 3 },
      { x1: 24, y1: 3, x2: 24, y2: 5 },
      { x1: 28, y1: 3, x2: 28, y2: 5 },
      { x1: 24, y1: 5, x2: 28, y2: 5 },
      // Middle right
      { x1: 28, y1: 1, x2: 34, y2: 1 },
      { x1: 31, y1: 1, x2: 31, y2: 5 },
      { x1: 31, y1: 3, x2: 37, y2: 3 },
      { x1: 34, y1: 5, x2: 37, y2: 5 },
      { x1: 37, y1: 5, x2: 37, y2: 6 },
      // Right section
      { x1: 39, y1: 2, x2: 44, y2: 2 },
      { x1: 39, y1: 4, x2: 43, y2: 4 },
      { x1: 43, y1: 4, x2: 43, y2: 6 },
      { x1: 45, y1: 6, x2: 47, y2: 6 },
      { x1: 47, y1: 2, x2: 51, y2: 2 },
      { x1: 47, y1: 4, x2: 51, y2: 4 },
      { x1: 47, y1: 6, x2: 51, y2: 6 },
    ];

    // Seed contribution dots
    const dots: { x: number; y: number; active: boolean; density: number }[] = [];
    for (let c = 0; c < cols; c++) {
      for (let r = 0; r < rows; r++) {
        let density = 0;
        if ((c > 40 && c < 48) || (c > 32 && c < 37) || (c === 0 && r < 3)) {
          density = Math.floor(Math.random() * 3) + 2;
        } else if (Math.random() > 0.8) {
          density = 1;
        }
        dots.push({ x: c, y: r, active: true, density });
      }
    }

    // Entities
    let pacman = { x: 28, y: 6, px: 28 * 16, py: 6 * 16, mouth: 0.2, mouthDir: 1, dir: -1 };
    const ghosts = [
      { name: 'Blinky', color: '#EF4444', x: 27, y: 2, px: 27 * 16, py: 2 * 16, dir: 1 },
      { name: 'Pinky', color: '#F472B6', x: 25, y: 4, px: 25 * 16, py: 4 * 16, dir: -1 },
      { name: 'Inky', color: '#38BDF8', x: 26, y: 4, px: 26 * 16, py: 4 * 16, dir: 1 },
      { name: 'Clyde', color: '#FB923C', x: 27, y: 4, px: 27 * 16, py: 4 * 16, dir: -1 },
    ];

    let animationId: number;

    const draw = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      // 1. Draw Background Contribution Cells
      dots.forEach((dot) => {
        const x = dot.x * (cellSize + gap);
        const y = dot.y * (cellSize + gap);

        let fill = isLightMode ? '#F0F5F2' : '#0B1416';
        if (dot.density === 1) fill = isLightMode ? '#C8E6D9' : '#143831';
        if (dot.density === 2) fill = isLightMode ? '#7DC6A8' : '#1C5B4E';
        if (dot.density === 3) fill = isLightMode ? '#349B78' : '#2A8270';
        if (dot.density >= 4) fill = isLightMode ? '#0D604B' : '#47B68D';

        ctx.fillStyle = fill;
        ctx.beginPath();
        ctx.roundRect(x, y, cellSize, cellSize, 2);
        ctx.fill();

        // Small food pellet if dot active
        if (dot.active && (dot.x + dot.y) % 3 === 0) {
          ctx.fillStyle = isLightMode ? '#0D604B' : '#8DE0C1';
          ctx.beginPath();
          ctx.arc(x + cellSize / 2, y + cellSize / 2, 1.8, 0, Math.PI * 2);
          ctx.fill();
        }
      });

      // 2. Draw Maze Wall Lines (white glowing lines matching Screenshot 192305.png)
      ctx.strokeStyle = isLightMode ? '#0D604B' : '#F0F3EE';
      ctx.lineWidth = 2.2;
      ctx.lineCap = 'round';
      ctx.beginPath();
      mazeWalls.forEach((w) => {
        const sx = w.x1 * (cellSize + gap) + cellSize / 2;
        const sy = w.y1 * (cellSize + gap) + cellSize / 2;
        const ex = w.x2 * (cellSize + gap) + cellSize / 2;
        const ey = w.y2 * (cellSize + gap) + cellSize / 2;
        ctx.moveTo(sx, sy);
        ctx.lineTo(ex, ey);
      });
      ctx.stroke();

      // 3. Update & Draw Ghosts
      ghosts.forEach((ghost) => {
        if (isPacmanPlaying) {
          ghost.px += ghost.dir * 0.9;
          if (ghost.px > canvas.width - 20) ghost.dir = -1;
          if (ghost.px < 20) ghost.dir = 1;
        }

        const gx = ghost.px;
        const gy = ghost.py;

        // Ghost body
        ctx.fillStyle = ghost.color;
        ctx.beginPath();
        ctx.arc(gx + 6, gy + 5, 6, Math.PI, 0, false);
        ctx.lineTo(gx + 12, gy + 12);
        // wavy skirt
        ctx.lineTo(gx + 9, gy + 10);
        ctx.lineTo(gx + 6, gy + 12);
        ctx.lineTo(gx + 3, gy + 10);
        ctx.lineTo(gx, gy + 12);
        ctx.closePath();
        ctx.fill();

        // Eyes
        ctx.fillStyle = '#FFFFFF';
        ctx.beginPath();
        ctx.arc(gx + 4, gy + 4, 1.8, 0, Math.PI * 2);
        ctx.arc(gx + 8, gy + 4, 1.8, 0, Math.PI * 2);
        ctx.fill();
        ctx.fillStyle = '#1E3A8A';
        ctx.beginPath();
        ctx.arc(gx + 4 + ghost.dir, gy + 4, 1, 0, Math.PI * 2);
        ctx.arc(gx + 8 + ghost.dir, gy + 4, 1, 0, Math.PI * 2);
        ctx.fill();
      });

      // 4. Update & Draw Pac-Man
      if (isPacmanPlaying) {
        pacman.px += pacman.dir * 1.4;
        if (pacman.px < 10) pacman.dir = 1;
        if (pacman.px > canvas.width - 20) pacman.dir = -1;

        // Animate mouth
        pacman.mouth += 0.04 * pacman.mouthDir;
        if (pacman.mouth > 0.35 || pacman.mouth < 0.05) pacman.mouthDir *= -1;

        // Eat dots on contact
        const currentGridX = Math.round(pacman.px / (cellSize + gap));
        const currentGridY = Math.round(pacman.py / (cellSize + gap));
        const targetDot = dots.find((d) => d.x === currentGridX && d.y === currentGridY);
        if (targetDot) targetDot.active = false;
      }

      // Render Pac-Man (iconic yellow champing character)
      const px = pacman.px + 7;
      const py = pacman.py + 7;
      const angleOffset = pacman.dir === 1 ? 0 : Math.PI;

      ctx.fillStyle = '#FACC15'; // classic arcade yellow
      ctx.beginPath();
      ctx.arc(
        px,
        py,
        6.5,
        angleOffset + pacman.mouth * Math.PI,
        angleOffset + (2 - pacman.mouth) * Math.PI
      );
      ctx.lineTo(px, py);
      ctx.closePath();
      ctx.fill();

      animationId = requestAnimationFrame(draw);
    };

    animationId = requestAnimationFrame(draw);
    return () => cancelAnimationFrame(animationId);
  }, [pacmanOpen, isLightMode, isPacmanPlaying]);

  // ----------------------------------------------------
  // 3. 3D ISOMETRIC YEAR VIEW
  // ----------------------------------------------------
  useEffect(() => {
    if (!isometricOpen) return;
    const canvas = isoCanvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    canvas.width = 820;
    canvas.height = 200;

    ctx.clearRect(0, 0, canvas.width, canvas.height);

    const cols = 42;
    const rows = 7;
    const originX = 410;
    const originY = 40;
    const tileW = 14;
    const tileH = 7;

    for (let c = 0; c < cols; c++) {
      for (let r = 0; r < rows; r++) {
        // Isometric projection
        const isoX = originX + (c - r) * (tileW / 2);
        const isoY = originY + (c + r) * (tileH / 2);

        // Height based on commits
        let height = 2;
        if (c > 35 && r > 2) height = 12 + ((c * 7 + r * 13) % 18);
        else if (c > 20 && Math.random() > 0.7) height = 6 + (c % 10);

        // Draw isometric pillar
        const topY = isoY - height;

        // Top face
        ctx.fillStyle = isLightMode ? '#0D604B' : height > 8 ? '#8DE0C1' : '#237865';
        ctx.beginPath();
        ctx.moveTo(isoX, topY);
        ctx.lineTo(isoX + tileW / 2, topY + tileH / 2);
        ctx.lineTo(isoX, topY + tileH);
        ctx.lineTo(isoX - tileW / 2, topY + tileH / 2);
        ctx.closePath();
        ctx.fill();

        // Left face
        ctx.fillStyle = isLightMode ? '#084838' : '#14463C';
        ctx.beginPath();
        ctx.moveTo(isoX - tileW / 2, topY + tileH / 2);
        ctx.lineTo(isoX, topY + tileH);
        ctx.lineTo(isoX, isoY + tileH);
        ctx.lineTo(isoX - tileW / 2, isoY + tileH / 2);
        ctx.closePath();
        ctx.fill();

        // Right face
        ctx.fillStyle = isLightMode ? '#0A5543' : '#1B5B4E';
        ctx.beginPath();
        ctx.moveTo(isoX, topY + tileH);
        ctx.lineTo(isoX + tileW / 2, topY + tileH / 2);
        ctx.lineTo(isoX + tileW / 2, isoY + tileH / 2);
        ctx.lineTo(isoX, isoY + tileH);
        ctx.closePath();
        ctx.fill();
      }
    }
  }, [isometricOpen, isLightMode]);

  return (
    <section className="mb-12">
      {/* Top Timeline / Ruler matching Screenshot 192305.png */}
      <div className="flex items-center space-x-1.5 overflow-hidden mb-6 opacity-60 font-mono text-[10px] select-none">
        <span className="shrink-0">—</span>
        {Array.from({ length: 36 }).map((_, i) => (
          <React.Fragment key={i}>
            <span className="opacity-40">·</span>
            {i === 14 ? (
              <span className={`font-bold inline-block w-2.5 h-2.5 rounded-full border ${
                isLightMode ? 'bg-[#0D604B] border-white' : 'bg-[#8DE0C1] border-black'
              }`} />
            ) : null}
          </React.Fragment>
        ))}
      </div>

      {/* Section Title matching Screenshot 192305.png: "Contribution art" */}
      <div className="mb-6">
        <h2 className="text-2xl sm:text-3xl font-bold tracking-tight">Contribution art</h2>
        <div className={`mt-2 h-[1px] w-full ${isLightMode ? 'bg-[#BAD6CB]' : 'bg-[#1B3937]'}`} />
      </div>

      {/* 1. Snake Live Animation Container */}
      <div
        className={`p-6 sm:p-7 rounded-2xl sm:rounded-3xl border mb-6 transition-all ${
          isLightMode
            ? 'bg-white border-[#BAD6CB] shadow-sm'
            : 'bg-[#080D0F] border-[#1B3937] shadow-xl'
        }`}
      >
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-2">
            <span className={`inline-block w-2 h-2 rounded-full ${
              isLightMode ? 'bg-[#0D604B]' : 'bg-[#8DE0C1]'
            }`} />
            <span className="text-xs font-mono font-bold uppercase tracking-wider opacity-80">
              Live Animated Snake Path
            </span>
          </div>

          <div className="flex items-center space-x-2">
            <button
              onClick={() => setIsSnakePlaying(!isSnakePlaying)}
              className={`p-1.5 rounded-lg border text-xs font-mono flex items-center space-x-1 cursor-pointer transition-all ${
                isLightMode
                  ? 'border-[#BAD6CB] bg-[#F4F8F6] text-[#0D604B] hover:bg-[#E2F0EA]'
                  : 'border-[#1B3937] bg-[#101B1D] text-[#8DE0C1] hover:bg-[#14272A]'
              }`}
            >
              {isSnakePlaying ? <Pause className="w-3.5 h-3.5" /> : <Play className="w-3.5 h-3.5" />}
              <span className="text-[11px] hidden sm:inline">{isSnakePlaying ? 'Pause' : 'Play'}</span>
            </button>
          </div>
        </div>

        {/* Snake Canvas Area */}
        <div className="overflow-x-auto pb-2 flex justify-center">
          <canvas
            ref={snakeCanvasRef}
            className="rounded-lg shadow-inner max-w-full"
            style={{ imageRendering: 'pixelated' }}
          />
        </div>

        {/* Scrubber / Progress Bar below snake matching Screenshot 192305.png */}
        <div className="mt-4 pt-2">
          <div className={`w-full h-2 rounded-full overflow-hidden ${
            isLightMode ? 'bg-gray-100' : 'bg-[#101B1D]'
          }`}>
            <div
              style={{ width: `${snakeProgress}%` }}
              className={`h-full rounded-full transition-all duration-150 ${
                isLightMode ? 'bg-[#0D604B]' : 'bg-[#8DE0C1]'
              }`}
            />
          </div>
        </div>
      </div>

      {/* 2. Pac-Man Section matching Screenshot 192305.png:
          "▼ Pac-Man — the contribution graph, played" */}
      <div
        className={`rounded-2xl sm:rounded-3xl border overflow-hidden mb-6 transition-all ${
          isLightMode ? 'bg-white border-[#BAD6CB]' : 'bg-[#080D0F] border-[#1B3937]'
        }`}
      >
        <button
          onClick={() => setPacmanOpen(!pacmanOpen)}
          className={`w-full p-5 sm:p-6 text-left flex items-center justify-between transition-colors cursor-pointer ${
            isLightMode ? 'hover:bg-[#F4F8F6]' : 'hover:bg-[#101B1D]'
          }`}
        >
          <div className="flex items-center space-x-2.5">
            {pacmanOpen ? (
              <ChevronDown className={`w-4 h-4 ${isLightMode ? 'text-[#0D604B]' : 'text-[#8DE0C1]'}`} />
            ) : (
              <ChevronRight className="w-4 h-4 opacity-75" />
            )}
            <span className="font-bold text-base sm:text-lg">
              Pac-Man — the contribution graph, played
            </span>
          </div>

          <div className="flex items-center space-x-2">
            <span className={`text-xs font-mono px-2 py-0.5 rounded border ${
              isLightMode
                ? 'bg-[#E2F0EA] border-[#BAD6CB] text-[#0D604B]'
                : 'bg-[#101B1D] border-[#1B3937] text-[#8DE0C1]'
            }`}>
              Live 60 FPS Canvas
            </span>
          </div>
        </button>

        {pacmanOpen && (
          <div className="px-5 sm:px-6 pb-6 pt-1 border-t border-inherit">
            {/* Top Month Labels matching screenshot (Oct, Nov, Dec, Jan, Feb, Mar, Apr, May, Jun, Jul, Aug, Sep, Oct) */}
            <div className="overflow-x-auto">
              <div className="min-w-[830px]">
                <div className="flex justify-between text-[11px] font-mono opacity-65 mb-2 px-1">
                  {months.map((m, i) => (
                    <span key={i}>{m}</span>
                  ))}
                </div>

                {/* Pac-Man Live Canvas */}
                <div className="flex justify-center p-2 rounded-xl bg-black/10">
                  <canvas
                    ref={pacmanCanvasRef}
                    className="rounded-lg shadow-md max-w-full"
                    style={{ imageRendering: 'pixelated' }}
                  />
                </div>
              </div>
            </div>

            {/* Play / Pause Controller */}
            <div className="flex items-center justify-between mt-4 pt-3 border-t border-inherit text-xs font-mono">
              <span className="opacity-70">
                Interactive Pac-Man maze navigation across 52-week activity grid
              </span>
              <button
                onClick={() => setIsPacmanPlaying(!isPacmanPlaying)}
                className={`px-3 py-1.5 rounded-lg border flex items-center space-x-1.5 cursor-pointer ${
                  isLightMode
                    ? 'border-[#BAD6CB] bg-[#F4F8F6] text-[#0D604B] hover:bg-[#E2F0EA]'
                    : 'border-[#1B3937] bg-[#101B1D] text-[#8DE0C1] hover:bg-[#14272A]'
                }`}
              >
                {isPacmanPlaying ? <Pause className="w-3.5 h-3.5" /> : <Play className="w-3.5 h-3.5" />}
                <span>{isPacmanPlaying ? 'Pause Ghosts & Pac-Man' : 'Resume'}</span>
              </button>
            </div>
          </div>
        )}
      </div>

      {/* 3. Isometric Year matching Screenshot 192305.png:
          "▶ Isometric year — contributions in 3D" */}
      <div
        className={`rounded-2xl sm:rounded-3xl border overflow-hidden transition-all ${
          isLightMode ? 'bg-white border-[#BAD6CB]' : 'bg-[#080D0F] border-[#1B3937]'
        }`}
      >
        <button
          onClick={() => setIsometricOpen(!isometricOpen)}
          className={`w-full p-5 sm:p-6 text-left flex items-center justify-between transition-colors cursor-pointer ${
            isLightMode ? 'hover:bg-[#F4F8F6]' : 'hover:bg-[#101B1D]'
          }`}
        >
          <div className="flex items-center space-x-2.5">
            {isometricOpen ? (
              <ChevronDown className={`w-4 h-4 ${isLightMode ? 'text-[#0D604B]' : 'text-[#8DE0C1]'}`} />
            ) : (
              <ChevronRight className="w-4 h-4 opacity-75" />
            )}
            <span className="font-bold text-base sm:text-lg">
              Isometric year — contributions in 3D
            </span>
          </div>

          <div className="flex items-center space-x-2">
            <Box className="w-4 h-4 opacity-60" />
            <span className="text-xs font-mono opacity-60">Spatial projection</span>
          </div>
        </button>

        {isometricOpen && (
          <div className="px-5 sm:px-6 pb-6 pt-1 border-t border-inherit">
            <div className="overflow-x-auto flex justify-center p-3 rounded-xl bg-black/10">
              <canvas
                ref={isoCanvasRef}
                className="rounded-lg shadow-md max-w-full"
              />
            </div>
            <p className="text-xs font-mono opacity-70 mt-3 text-center">
              3D isometric topology showing peak contribution elevations across 2024–2026.
            </p>
          </div>
        )}
      </div>
    </section>
  );
};
