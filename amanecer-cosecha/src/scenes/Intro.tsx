import React from 'react';
import {AbsoluteFill, useCurrentFrame} from 'remotion';
import {C, Camera, Dust, Sparks, Spectator, SkyRect, Stage, Urn, W, ease, easeIn, lerp} from '../lib/base';

type SceneProps = {readonly dur: number};

// ---------- Sala de cine (imagen ancla) ----------
const ROWS = [
	{y: 900, w: 100, h: 70},
	{y: 990, w: 115, h: 80},
	{y: 1100, w: 135, h: 95},
	{y: 1240, w: 160, h: 115},
	{y: 1440, w: 200, h: 150},
	{y: 1690, w: 250, h: 190},
];

const SeatRow: React.FC<{readonly y: number; readonly w: number; readonly h: number; readonly k: number}> = ({y, w, h, k}) => {
	const n = Math.ceil(W / w) + 2;
	const off = (k % 2) * (w / 2) - w;
	return (
		<g>
			{new Array(n).fill(0).map((_, i) => {
				const x = off + i * w + (W - (n - 2) * w) / 2;
				return (
					<g key={i}>
						<rect x={x + 6} y={y} width={w - 12} height={h} rx={w * 0.22} fill={C.crimson} />
						<rect x={x + 6} y={y} width={w - 12} height={h * 0.28} rx={w * 0.2} fill="#c9405a" opacity={0.6} />
						<rect x={x + 6} y={y + h * 0.7} width={w - 12} height={h * 0.3} fill={C.crimsonDark} opacity={0.7} />
					</g>
				);
			})}
		</g>
	);
};

const Theater: React.FC<{readonly screen?: number; readonly turn?: number}> = ({screen = 1, turn = 0}) => {
	const f = useCurrentFrame();
	const flicker = 0.9 + 0.1 * Math.sin(f * 0.7) * Math.sin(f * 0.23);
	const light = screen * flicker;
	return (
		<Stage bg={C.night}>
			<SkyRect id="th-bg" stops={[[0, '#0a1a1f'], [0.5, C.deep], [1, '#050b0d']]} />
			{/* pantalla */}
			<defs>
				<linearGradient id="th-screen" x1="0" y1="0" x2="1" y2="1">
					<stop offset="0%" stopColor="#f4fbf7" />
					<stop offset="100%" stopColor={C.haze} />
				</linearGradient>
				<linearGradient id="th-beam" x1="0" y1="0" x2="0" y2="1">
					<stop offset="0%" stopColor="#ffffff" stopOpacity="0" />
					<stop offset="100%" stopColor={C.haze} stopOpacity="0.35" />
				</linearGradient>
				<clipPath id="th-beam-clip">
					<polygon points="430,-20 650,-20 1010,800 70,800" />
				</clipPath>
			</defs>
			<rect x={40} y={170} width={1000} height={660} fill={C.haze} opacity={0.25 * light} filter="url(#soft)" />
			<rect x={90} y={220} width={900} height={560} rx={8} fill="#0d1517" />
			<rect x={90} y={220} width={900} height={560} rx={8} fill="url(#th-screen)" opacity={light} />
			{/* haz del proyector con polvo brillante */}
			<polygon points="430,-20 650,-20 1010,800 70,800" fill="url(#th-beam)" opacity={light} filter="url(#blur4)" />
			<g clipPath="url(#th-beam-clip)" opacity={light}>
				<Dust n={110} seed="th-dust" box={[60, 0, 960, 820]} color="#ffffff" vy={-0.3} vx={0.4} />
			</g>
			{/* filas de butacas carmesí */}
			{ROWS.slice(0, 3).map((r, k) => (
				<SeatRow key={k} k={k} {...r} />
			))}
			<Spectator x={540} y={1340} w={300} turn={turn} rim={light > 0.2 ? '#e8f4ef' : C.teal} />
			{ROWS.slice(3).map((r, k) => (
				<SeatRow key={k} k={k + 3} {...r} />
			))}
			{/* luz de la pantalla sobre las butacas */}
			<rect x={0} y={820} width={W} height={1100} fill={C.haze} opacity={0.08 * light} />
		</Stage>
	);
};

export const CinemaPush: React.FC<SceneProps> = ({dur}) => (
	<Camera dur={dur} origin={[540, 1120]} scale={[1, 1.55]} easing={ease}>
		<Theater />
	</Camera>
);

export const CinemaFinal: React.FC<SceneProps> = ({dur}) => (
	<Camera dur={dur} origin={[540, 1120]} scale={[1.3, 1.45]}>
		<Theater />
	</Camera>
);

export const CinemaTurn: React.FC<SceneProps> = ({dur}) => {
	const f = useCurrentFrame();
	return (
		<Camera dur={dur} origin={[540, 1120]} scale={[1.45, 1.55]}>
			<Theater turn={lerp(f, [0.2 * dur, 0.8 * dur], [0, 0.85], ease)} />
		</Camera>
	);
};

export const CinemaOff: React.FC<SceneProps> = ({dur}) => {
	const f = useCurrentFrame();
	return (
		<AbsoluteFill style={{background: '#000'}}>
			<AbsoluteFill style={{opacity: lerp(f, [0.3 * dur, dur], [1, 0])}}>
				<Camera dur={dur} origin={[540, 1120]} scale={[1.55, 1.58]}>
					<Theater turn={0.85} screen={lerp(f, [0, 0.85 * dur], [1, 0])} />
				</Camera>
			</AbsoluteFill>
		</AbsoluteFill>
	);
};

// ---------- Primer plano del perfil, luz en el ojo ----------
export const EyeProfile: React.FC<SceneProps> = ({dur}) => {
	const f = useCurrentFrame();
	const grow = lerp(f, [0.25 * dur, dur], [10, 2600], easeIn);
	return (
		<Camera dur={dur} origin={[600, 900]} scale={[1, 1.15]}>
			<Stage bg={C.night}>
				<SkyRect id="eye-bg" stops={[[0, '#0b1c20'], [1, '#06100f']]} />
				{/* luz que viene de la pantalla, a la derecha */}
				<rect x={600} y={0} width={600} height={1920} fill={C.haze} opacity={0.18} filter="url(#soft)" />
				{/* capucha mostaza */}
				<path d="M-60 1500 C200 1420 520 1480 760 1920 L-60 1920 Z" fill={C.mustard} />
				<path d="M-60 1600 C200 1540 460 1600 620 1920 L-60 1920 Z" fill={C.mustardDark} opacity={0.6} />
				{/* perfil (forma estilizada, sin parecido con nadie) */}
				<path
					d="M-60 240 C200 160 540 230 600 520 L640 760 C652 800 640 826 640 846 L724 984 L652 1014 C684 1060 672 1092 652 1112 C674 1150 664 1240 604 1300 C560 1360 520 1380 480 1420 L470 1560 L-60 1560 Z"
					fill="#3b2a22"
					stroke="#dff1ea"
					strokeWidth={5}
					strokeOpacity={0.7}
				/>
				{/* pelo y barba */}
				<path d="M-60 240 C200 160 540 230 600 520 C520 430 300 420 200 520 C120 600 60 560 -60 640 Z" fill={C.hair} />
				<path d="M652 1112 C674 1150 664 1240 604 1300 C560 1360 520 1380 480 1420 L420 1340 C520 1300 580 1220 600 1130 Z" fill="#1f1713" opacity={0.85} />
				{/* ojo */}
				<path d="M540 880 Q590 846 628 884 Q590 904 540 880 Z" fill="#f2efe6" />
				<circle cx={600} cy={880} r={13} fill="#24170f" />
				<circle cx={606} cy={876} r={grow} fill="url(#whiteGlow)" />
				<circle cx={606} cy={876} r={grow * 0.55} fill="#ffffff" />
			</Stage>
		</Camera>
	);
};

// ---------- Vela sobre un pan, cocina humilde al amanecer ----------
const Flame: React.FC<{readonly x: number; readonly y: number; readonly s: number}> = ({x, y, s}) => {
	const f = useCurrentFrame();
	const sx = 1 + 0.1 * Math.sin(f * 0.9);
	const sy = 1 + 0.14 * Math.sin(f * 1.3 + 1);
	const lean = Math.sin(f * 0.5) * 6;
	return (
		<g transform={`translate(${x} ${y}) scale(${s})`}>
			<circle cx={0} cy={-30} r={160} fill="url(#warmGlow)" opacity={0.8} />
			<g transform={`rotate(${lean}) scale(${sx} ${sy})`}>
				<path d="M0 -110 C30 -60 34 -20 0 10 C-34 -20 -30 -60 0 -110 Z" fill={C.gold} filter="url(#glow)" />
				<path d="M0 -70 C14 -40 16 -16 0 4 C-16 -16 -14 -40 0 -70 Z" fill="#fff4c8" />
			</g>
		</g>
	);
};

export const CandleScene: React.FC<SceneProps> = ({dur}) => (
	<Camera dur={dur} origin={[540, 1100]} scale={[1.05, 1.2]}>
		<Stage bg="#2a1d16">
			{/* paredes de madera */}
			{new Array(9).fill(0).map((_, i) => (
				<rect key={i} x={i * 120} y={0} width={120} height={1400} fill={i % 2 ? '#3d2b20' : '#46322424'} stroke="#24180f" strokeWidth={4} />
			))}
			<rect x={0} y={0} width={1080} height={1400} fill="#3d2b20" opacity={0.6} />
			{/* ventana con amanecer */}
			<SkyRect id="dawn" x={110} y={220} w={360} h={460} stops={[[0, '#3f5f6a'], [0.55, '#d98e5a'], [1, C.gold]]} />
			<rect x={110} y={220} width={360} height={460} fill="none" stroke="#24180f" strokeWidth={22} />
			<line x1={290} y1={220} x2={290} y2={680} stroke="#24180f" strokeWidth={14} />
			<polygon points="110,680 470,680 900,1500 340,1500" fill={C.gold} opacity={0.12} filter="url(#blur4)" />
			<Dust n={50} seed="kitchen" box={[100, 600, 800, 900]} color={C.goldLight} size={[1, 3]} />
			{/* mesa */}
			<rect x={0} y={1380} width={1080} height={540} fill="#5b3f2b" />
			<rect x={0} y={1380} width={1080} height={26} fill="#7a5638" />
			{/* pan */}
			<ellipse cx={540} cy={1440} rx={220} ry={34} fill="#000" opacity={0.35} />
			<path d="M330 1420 C330 1260 750 1260 750 1420 Z" fill="#b97a3d" />
			<path d="M380 1330 Q420 1300 450 1340 M500 1310 Q540 1280 570 1320 M620 1330 Q660 1300 690 1345" stroke="#8a5424" strokeWidth={10} fill="none" />
			{/* vela */}
			<rect x={515} y={1070} width={50} height={230} rx={6} fill="#f0e2c4" />
			<rect x={515} y={1070} width={14} height={230} fill="#ffffff" opacity={0.4} />
			<line x1={540} y1={1070} x2={540} y2={1048} stroke="#222" strokeWidth={4} />
			<Flame x={540} y={1050} s={1} />
			<Sparks x={540} y={950} n={26} seed="candle" dist={220} life={30} spread={1.4} gravity={-30} size={3.5} />
		</Stage>
	</Camera>
);

// ---------- El humo dibuja una urna de vidrio ----------
export const SmokeUrn: React.FC<SceneProps> = ({dur}) => {
	const f = useCurrentFrame();
	const smoke = lerp(f, [0, 0.45 * dur], [0, 1], ease);
	const draw = lerp(f, [0.25 * dur, 0.75 * dur], [0, 1], ease);
	const glass = lerp(f, [0.55 * dur, 0.9 * dur], [0, 1]);
	const wob = Math.sin(f * 0.2) * 20;
	return (
		<Stage bg="#1b1512">
			<SkyRect id="smk-bg" stops={[[0, '#14262a'], [1, '#2a1d16']]} />
			<rect x={0} y={1700} width={1080} height={220} fill="#3b2a1e" />
			{/* vela pequeña abajo */}
			<rect x={528} y={1640} width={24} height={110} fill="#f0e2c4" />
			<circle cx={540} cy={1620} r={70} fill="url(#warmGlow)" />
			<path d="M540 1590 C552 1610 552 1625 540 1636 C528 1625 528 1610 540 1590 Z" fill={C.gold} />
			{/* columna de humo */}
			<path
				d={`M540 1590 C${500 + wob} 1450 ${600 - wob} 1300 540 1150 C${480 + wob} 1000 ${600 - wob} 900 540 760`}
				stroke="#cfd8d4"
				strokeWidth={34}
				fill="none"
				opacity={0.45}
				filter="url(#soft)"
				pathLength={1}
				strokeDasharray="1 1"
				strokeDashoffset={1 - smoke}
			/>
			<path
				d={`M540 1590 C${500 + wob} 1450 ${600 - wob} 1300 540 1150 C${480 + wob} 1000 ${600 - wob} 900 540 760`}
				stroke="#eef3f0"
				strokeWidth={6}
				fill="none"
				opacity={0.5}
				pathLength={1}
				strokeDasharray="1 1"
				strokeDashoffset={1 - smoke}
			/>
			<g filter="url(#glow)">
				<Urn x={540} y={1500} h={900} draw={draw} glass={glass} agitation={1.4} stroke="#e8f1ee" seed="smoke" />
			</g>
		</Stage>
	);
};

// ---------- Pantalla gigante en la plaza gris, EN VIVO ----------
export const PlazaScreen: React.FC<SceneProps> = ({dur}) => {
	const f = useCurrentFrame();
	const blink = Math.floor(f / 6) % 2 === 0 ? 1 : 0.25;
	return (
		<Camera dur={dur} origin={[540, 720]} scale={[1.5, 1]} easing={ease}>
			<Stage bg="#5d6668">
				<SkyRect id="pl-sky" stops={[[0, '#7c8788'], [0.6, '#596365'], [1, '#3d4547']]} />
				{/* edificios grises */}
				{[0, 1, 2, 3].map((i) => (
					<rect key={i} x={i * 70 - 40} y={500 + (i % 2) * 120} width={90} height={1000} fill="#41494b" />
				))}
				{[0, 1, 2, 3].map((i) => (
					<rect key={i} x={830 + i * 70} y={480 + ((i + 1) % 2) * 140} width={90} height={1000} fill="#41494b" />
				))}
				{/* suelo de la plaza */}
				<polygon points="0,1350 1080,1350 1080,1920 0,1920" fill="#4a5254" />
				{new Array(8).fill(0).map((_, i) => (
					<line key={i} x1={540} y1={1350} x2={-400 + i * 270} y2={1920} stroke="#3c4345" strokeWidth={4} />
				))}
				{/* estructura y pantalla gigante */}
				<rect x={240} y={1000} width={30} height={360} fill="#2b3133" />
				<rect x={810} y={1000} width={30} height={360} fill="#2b3133" />
				<rect x={110} y={400} width={860} height={620} fill="#1d2325" />
				<rect x={130} y={420} width={820} height={580} fill="#14282b" />
				<rect x={130} y={420} width={820} height={580} fill={C.tealMid} opacity={0.4} />
				<Urn x={540} y={960} h={480} seed="plaza" />
				<circle cx={900} cy={470} r={22} fill={C.red} opacity={blink} filter="url(#glow)" />
				{/* multitud pequeña */}
				{new Array(40).fill(0).map((_, i) => (
					<g key={i}>
						<circle cx={20 + i * 27} cy={1690 + (i % 3) * 30} r={14} fill="#1e2324" />
						<rect x={6 + i * 27} y={1702 + (i % 3) * 30} width={28} height={300} rx={10} fill="#1e2324" />
					</g>
				))}
				<Dust n={30} seed="plaza-dust" color="#c9cfcd" vx={2} vy={0.2} opacity={0.4} glow={false} />
			</Stage>
		</Camera>
	);
};

