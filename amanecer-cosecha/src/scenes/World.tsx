import React from 'react';
import {AbsoluteFill, random, useCurrentFrame} from 'remotion';
import {C, Camera, Dust, Figure, SkyRect, Spectator, Stage, ease, inOut, lerp} from '../lib/base';
import {MAP, MapBase, MapIcon, REGIONS} from '../lib/map';

type SceneProps = {readonly dur: number};

const MapBg: React.FC = () => (
	<>
		<SkyRect id="map-bg" stops={[[0, '#163338'], [0.5, '#1f4448'], [1, '#0e2226']]} />
		{/* papel envejecido */}
		<rect x={30} y={240} width={1020} height={1440} rx={20} fill="#c8b98f" opacity={0.12} filter="url(#paint)" />
	</>
);

// ---------- Pulsos de luz desde la capital ----------
export const MapPulses: React.FC<SceneProps> = ({dur}) => {
	const f = useCurrentFrame();
	return (
		<Camera dur={dur} origin={[540, 960]} scale={[1.12, 1]}>
			<Stage bg={C.deep}>
				<MapBg />
				<MapBase lines={0.35}>
					{[0, 1, 2].map((k) => {
						const t = ((f + k * 14) % 42) / 42;
						return (
							<ellipse
								key={k}
								cx={MAP.cx}
								cy={MAP.cy}
								rx={MAP.rin + t * 420}
								ry={(MAP.rin + t * 420) * 1.3}
								fill="none"
								stroke={C.gold}
								strokeWidth={6}
								opacity={(1 - t) * 0.7}
								filter="url(#glow)"
							/>
						);
					})}
					{REGIONS.map((r, i) => {
						const t = ((f * 1.2 + i * 5) % 30) / 30;
						return (
							<circle
								key={i}
								cx={MAP.cx + (r.c[0] - MAP.cx) * t}
								cy={MAP.cy + (r.c[1] - MAP.cy) * t}
								r={10}
								fill={C.goldLight}
								filter="url(#glow)"
							/>
						);
					})}
				</MapBase>
			</Stage>
		</Camera>
	);
};

// ---------- Filas de siluetas caminan hacia la capital ----------
export const MapMarch: React.FC<SceneProps> = ({dur}) => {
	const f = useCurrentFrame();
	return (
		<Camera dur={dur} origin={[540, 960]} scale={[1, 1.08]}>
			<Stage bg={C.deep}>
				<MapBg />
				<MapBase lines={0.8}>
					{REGIONS.map((r, i) =>
						[0, 1, 2].map((k) => {
							const t = lerp(f, [0, dur], [0.05, 0.55]) + k * 0.12;
							const px = r.c[0] + (MAP.cx - r.c[0]) * t;
							const py = r.c[1] + (MAP.cy - r.c[1]) * t;
							return (
								<g key={`${i}-${k}`}>
									{/* huellas que se encienden */}
									{[1, 2, 3, 4].map((q) => {
										const tq = t - q * 0.035;
										if (tq < 0) return null;
										return (
											<circle
												key={q}
												cx={r.c[0] + (MAP.cx - r.c[0]) * tq}
												cy={r.c[1] + (MAP.cy - r.c[1]) * tq + 4}
												r={4}
												fill={C.goldLight}
												opacity={0.9 - q * 0.2}
												filter="url(#glow)"
											/>
										);
									})}
									<Figure x={px} y={py} h={44} color="#101416" walk={f * 0.5 + i + k} rim={C.goldLight} />
								</g>
							);
						}),
					)}
				</MapBase>
			</Stage>
		</Camera>
	);
};

// ---------- Arena circular: las luces se apagan hasta quedar una ----------
export const ArenaLights: React.FC<SceneProps> = ({dur}) => {
	const f = useCurrentFrame();
	const n = 24;
	const lights = new Array(n).fill(0).map((_, i) => {
		const a = random(`ar-a-${i}`) * Math.PI * 2;
		const r = 60 + Math.sqrt(random(`ar-r-${i}`)) * 340;
		return {x: 540 + Math.cos(a) * r, y: 960 + Math.sin(a) * r, order: random(`ar-o-${i}`)};
	});
	// La última luz (índice 0) nunca se apaga.
	const sorted = [...lights.keys()].filter((i) => i !== 0).sort((a, b) => lights[a].order - lights[b].order);
	return (
		<Camera dur={dur} origin={[540, 960]} scale={[1, 1.25]} easing={inOut}>
			<Stage bg="#0a1612">
				<SkyRect id="ar-bg" stops={[[0, '#0c1b17'], [1, '#07100d']]} />
				<circle cx={540} cy={960} r={470} fill="#1f3a2c" filter="url(#paint)" />
				{new Array(40).fill(0).map((_, i) => {
					const a = random(`tree-${i}`) * Math.PI * 2;
					const r = Math.sqrt(random(`tree-r-${i}`)) * 420;
					return <circle key={i} cx={540 + Math.cos(a) * r} cy={960 + Math.sin(a) * r} r={30 + random(`tree-s-${i}`) * 40} fill="#183026" />;
				})}
				<circle cx={540} cy={960} r={470} fill="none" stroke="#5b6b62" strokeWidth={20} />
				<circle cx={540} cy={960} r={500} fill="none" stroke="#3a4741" strokeWidth={12} />
				{lights.map((l, i) => {
					const rank = sorted.indexOf(i);
					const offAt = rank < 0 ? Infinity : 6 + rank * ((dur - 30) / sorted.length);
					const on = f < offAt ? 1 : lerp(f, [offAt, offAt + 5], [1, 0]);
					const last = i === 0 ? 1 + 0.3 * Math.sin(f * 0.3) : 1;
					return (
						<g key={i} opacity={on}>
							<circle cx={l.x} cy={l.y} r={40 * last} fill="url(#warmGlow)" />
							<circle cx={l.x} cy={l.y} r={8 * last} fill={C.goldLight} />
						</g>
					);
				})}
			</Stage>
		</Camera>
	);
};

// ---------- Pueblo minero gris ----------
const Houses: React.FC<{readonly y: number; readonly s: number; readonly seed: string; readonly color: string}> = ({y, s, seed, color}) => (
	<g>
		{new Array(Math.ceil(1200 / (150 * s))).fill(0).map((_, i) => {
			const w = (110 + random(`${seed}-w-${i}`) * 40) * s;
			const h = (90 + random(`${seed}-h-${i}`) * 50) * s;
			const x = i * 150 * s - 40;
			return (
				<g key={i}>
					<rect x={x} y={y - h} width={w} height={h + 400} fill={color} stroke="#24292b" strokeWidth={3} />
					<polygon points={`${x - 10},${y - h} ${x + w / 2},${y - h - 60 * s} ${x + w + 10},${y - h}`} fill="#2f3537" />
					{[0, 1, 2].map((p) => (
						<line key={p} x1={x + (w / 4) * (p + 1)} y1={y - h} x2={x + (w / 4) * (p + 1)} y2={y + 400} stroke="#2f3537" strokeWidth={2} />
					))}
					<rect x={x + w * 0.35} y={y - h * 0.6} width={w * 0.3} height={h * 0.3} fill="#1a1f21" />
				</g>
			);
		})}
	</g>
);

const Smoke: React.FC<{readonly x: number; readonly y: number; readonly seed: string}> = ({x, y, seed}) => {
	const f = useCurrentFrame();
	return (
		<g filter="url(#soft)">
			{new Array(8).fill(0).map((_, i) => {
				const t = ((f * 0.8 + i * 12) % 96) / 96;
				return (
					<circle
						key={i}
						cx={x + t * 160 + random(`${seed}-${i}`) * 30}
						cy={y - t * 520}
						r={40 + t * 110}
						fill="#141718"
						opacity={0.85 * (1 - t)}
					/>
				);
			})}
		</g>
	);
};

const MiningBackdrop: React.FC = () => (
	<>
		<SkyRect id="mine-sky" stops={[[0, '#4c5557'], [0.5, '#6f797a'], [1, '#8a9291']]} />
		{/* montaña y entrada de la mina */}
		<path d="M-50 1100 C150 700 380 560 600 620 C800 680 960 760 1130 980 L1130 1300 L-50 1300 Z" fill="#33393b" filter="url(#paint)" />
		<path d="M380 1150 L380 980 Q470 900 560 980 L560 1150 Z" fill="#0b0d0e" />
		<path d="M370 1150 L370 975 Q470 880 570 975 L570 1150" stroke="#5a4330" strokeWidth={18} fill="none" />
		<Smoke x={760} y={760} seed="s1" />
		<Smoke x={220} y={860} seed="s2" />
	</>
);

export const MiningTown: React.FC<SceneProps> = ({dur}) => (
	<Camera dur={dur} origin={[470, 1050]} scale={[1, 1.12]}>
		<Stage bg="#5f6869">
			<MiningBackdrop />
			<Houses y={1280} s={0.8} seed="h1" color="#545b5c" />
			<Houses y={1560} s={1.2} seed="h2" color="#61686a" />
			<rect x={0} y={1560} width={1080} height={400} fill="#2d3234" />
			{/* ráfagas de polvo de carbón */}
			<Dust n={140} seed="coal" color="#1a1c1d" vx={9} vy={0.6} size={[2, 6]} opacity={0.7} glow={false} />
		</Stage>
	</Camera>
);

// ---------- El Espectador mira salir al joven de la mina ----------
export const MineExit: React.FC<SceneProps> = ({dur}) => {
	const f = useCurrentFrame();
	const lamp = (k: number) => (random(`lamp-${k}-${Math.floor(f / 3)}`) > 0.25 ? 1 : 0.2);
	const walk = lerp(f, [0, dur], [0, 1]);
	return (
		<Camera dur={dur} origin={[540, 1000]} scale={[1.05, 1.15]}>
			<Stage bg="#5f6869">
				<SkyRect id="me-sky" stops={[[0, '#4c5557'], [1, '#7c8586']]} />
				<path d="M-50 900 C200 640 800 600 1130 880 L1130 1300 L-50 1300 Z" fill="#33393b" filter="url(#paint)" />
				<path d="M420 1110 L420 900 Q540 800 660 900 L660 1110 Z" fill="#0b0d0e" />
				<path d="M408 1110 L408 892 Q540 780 672 892 L672 1110" stroke="#5a4330" strokeWidth={20} fill="none" />
				{[0, 1].map((k) => (
					<g key={k} opacity={lamp(k)}>
						<circle cx={k ? 700 : 380} cy={900} r={70} fill="url(#warmGlow)" />
						<circle cx={k ? 700 : 380} cy={900} r={12} fill={C.goldLight} />
					</g>
				))}
				{/* calle */}
				<polygon points="440,1110 640,1110 1080,1920 0,1920" fill="#3a3f41" />
				<polygon points="0,1100 440,1110 0,1920" fill="#4c5354" />
				<polygon points="1080,1100 640,1110 1080,1920" fill="#4c5354" />
				{/* el joven: pelo oscuro, camisa de trabajo gris */}
				<Figure x={540} y={1100 + walk * 160} h={150 + walk * 90} color="#1c2022" shirt="#7d8586" walk={f * 0.35} rim={C.goldLight} />
				<Dust n={60} seed="me-coal" color="#1a1c1d" vx={5} vy={0.3} size={[2, 5]} opacity={0.6} glow={false} />
				{/* el Espectador, de espaldas en primer plano */}
				<Spectator x={260} y={2000} w={520} rim="#c7d0cd" />
			</Stage>
		</Camera>
	);
};

// ---------- Pradera soleada con árbol y gansos ----------
const Meadow: React.FC<{readonly sun?: number; readonly pointing?: boolean; readonly seeds?: boolean; readonly headDown?: number}> = ({sun = 1, pointing = false, seeds = true, headDown = 0}) => {
	const f = useCurrentFrame();
	return (
		<>
			<SkyRect id="md-sky" stops={[[0, '#7fb6b0'], [0.6, '#e6cf8f'], [1, '#f2c14e']]} />
			<circle cx={830} cy={520} r={300} fill="url(#warmGlow)" opacity={sun} />
			<path d="M-50 1150 C250 1020 600 1080 1130 980 L1130 1920 L-50 1920 Z" fill="#6f9a55" filter="url(#paint)" />
			<path d="M-50 1350 C300 1240 700 1300 1130 1200 L1130 1920 L-50 1920 Z" fill="#5c8746" filter="url(#paint)" />
			{/* árbol grande */}
			<path d="M250 1420 C270 1250 250 1080 230 940 L300 940 C300 1080 320 1250 340 1420 Z" fill="#4a3222" />
			<g filter="url(#paint)">
				{[
					[270, 820, 230],
					[120, 900, 160],
					[420, 900, 170],
					[200, 700, 170],
					[360, 720, 170],
				].map(([x, y, r], i) => (
					<circle key={i} cx={x} cy={y} r={r} fill={i % 2 ? '#3f6b37' : '#4b7a40'} />
				))}
			</g>
			{/* gansos blancos */}
			{[0, 1, 2, 3].map((i) => {
				const gx = 700 + i * 80 - ((f * 0.6) % 40) + Math.sin(i) * 20;
				const gy = 1360 + (i % 2) * 40;
				return (
					<g key={i} transform={`translate(${gx} ${gy})`}>
						<ellipse cx={0} cy={0} rx={30} ry={18} fill="#f4f1e8" />
						<path d="M18 -6 Q28 -40 36 -40" stroke="#f4f1e8" strokeWidth={8} fill="none" />
						<path d="M36 -42 L48 -38 L36 -34 Z" fill={C.orange} />
					</g>
				);
			})}
			{/* la pareja, sentada bajo el árbol, de espaldas */}
			<Figure x={300} y={1500} h={170} color="#24292b" shirt="#7d8586" headTilt={headDown * -25} />
			<Figure
				x={400}
				y={1500}
				h={160}
				color="#2a2422"
				hair="long"
				dress={['#7a4b6a', C.mustard, C.crimson, '#3f7c8a', '#6f9a55', '#c46a3a']}
				arms={pointing ? 'point' : 'down'}
			/>
			{seeds ? <Dust n={50} seed="seeds" color="#fffbe9" vx={2.5} vy={-0.5} size={[2, 4]} opacity={0.9} /> : null}
		</>
	);
};

export const MeadowScene: React.FC<SceneProps> = ({dur}) => (
	<Camera dur={dur} origin={[350, 1300]} scale={[1, 1.1]}>
		<Stage bg="#7fb6b0">
			<Meadow />
		</Stage>
	</Camera>
);

// Pueblo libre dibujado con trazos dorados en el cielo.
const GOLD_TOWN = [
	'M140 640 L140 520 L220 450 L300 520 L300 640',
	'M320 640 L320 480 L410 400 L500 480 L500 640',
	'M520 640 L520 540 L590 480 L660 540 L660 640',
	'M680 640 L680 470 L780 390 L880 470 L880 640',
	'M900 640 L900 540 L960 500 L1000 540 L1000 640',
	'M100 640 L1020 640',
	'M200 640 L200 580 L240 580 L240 640',
	'M560 640 L560 590 L620 590 L620 640',
	'M760 560 L800 560 L800 600 L760 600 Z',
	'M380 540 L440 540 L440 590 L380 590 Z',
	'M150 380 Q330 300 520 360 Q740 280 960 360',
];

const GoldTown: React.FC<{readonly draw: number; readonly crack?: number; readonly fall?: number}> = ({draw, crack = 0, fall = 0}) => (
	<g filter="url(#glow)">
		{GOLD_TOWN.map((d, i) => {
			const dx = (i % 2 ? 1 : -1) * fall * (40 + i * 12);
			const dy = fall * fall * (500 + i * 60);
			const rot = (i % 2 ? 1 : -1) * fall * (10 + i * 3);
			return (
				<path
					key={i}
					d={d}
					stroke={C.gold}
					strokeWidth={8}
					strokeLinecap="round"
					fill="none"
					pathLength={1}
					strokeDasharray="1 1"
					strokeDashoffset={1 - lerp(draw, [i * 0.05, i * 0.05 + 0.45], [0, 1])}
					transform={`translate(${dx} ${dy}) rotate(${rot} 560 520)`}
					opacity={1 - fall * 0.8}
				/>
			);
		})}
		{crack > 0 ? (
			<path
				d="M560 300 L520 420 L600 480 L540 560 L620 650 M520 420 L420 460 M600 480 L720 440 M540 560 L460 640"
				stroke="#ffffff"
				strokeWidth={5}
				fill="none"
				pathLength={1}
				strokeDasharray="1 1"
				strokeDashoffset={1 - crack}
				opacity={1 - fall}
			/>
		) : null}
	</g>
);

export const GoldenVision: React.FC<SceneProps> = ({dur}) => {
	const f = useCurrentFrame();
	return (
		<Camera dur={dur} origin={[540, 700]} scale={[1, 1.08]}>
			<Stage bg="#7fb6b0">
				<Meadow pointing seeds />
				<GoldTown draw={lerp(f, [0.1 * dur, 0.95 * dur], [0, 1], ease)} />
			</Stage>
		</Camera>
	);
};

export const VisionShatters: React.FC<SceneProps> = ({dur}) => {
	const f = useCurrentFrame();
	const crack = lerp(f, [0, 0.3 * dur], [0, 1], ease);
	const fall = lerp(f, [0.3 * dur, 0.8 * dur], [0, 1]);
	const dim = lerp(f, [0.3 * dur, dur], [0, 0.5]);
	return (
		<AbsoluteFill>
			<Camera dur={dur} origin={[540, 1300]} scale={[1.1, 1]}>
				<Stage bg="#7fb6b0">
					<Meadow sun={1 - dim} seeds={false} headDown={lerp(f, [0.3 * dur, 0.7 * dur], [0, 1], ease)} />
					<rect x={0} y={0} width={1080} height={1920} fill="#1d4248" opacity={dim} />
				</Stage>
			</Camera>
			<Stage>
				<GoldTown draw={1} crack={crack} fall={fall} />
			</Stage>
		</AbsoluteFill>
	);
};

// ---------- Fuegos artificiales sobre la capital ----------
export const Fireworks: React.FC<SceneProps> = () => {
	const f = useCurrentFrame();
	const bursts = [
		{x: 600, y: 520, at: 0},
		{x: 380, y: 640, at: 14},
		{x: 760, y: 420, at: 26},
		{x: 520, y: 360, at: 40},
	];
	return (
		<Stage bg="#0b1416">
			<SkyRect id="fw-sky" stops={[[0, '#081114'], [0.7, '#1b2b2c'], [1, '#3b3826']]} />
			{/* capital a lo lejos */}
			<ellipse cx={560} cy={1080} rx={420} ry={120} fill="url(#warmGlow)" />
			{[0, 1, 2, 3, 4, 5, 6, 7, 8].map((k) => (
				<rect key={k} x={380 + k * 40} y={1080 - (k % 4) * 40 - 60} width={26} height={140 + (k % 4) * 40} fill={C.gold} opacity={0.8} />
			))}
			{bursts.map((b, j) => {
				const t = lerp(f, [b.at, b.at + 26], [0, 1], ease);
				if (f < b.at) return null;
				return (
					<g key={j} filter="url(#glow)" opacity={1 - lerp(f, [b.at + 14, b.at + 30], [0, 1])}>
						{new Array(22).fill(0).map((_, i) => {
							const a = (i / 22) * Math.PI * 2;
							const r = t * 180;
							return <circle key={i} cx={b.x + Math.cos(a) * r} cy={b.y + Math.sin(a) * r + t * t * 40} r={5} fill={i % 3 ? C.gold : C.goldLight} />;
						})}
					</g>
				);
			})}
			{/* pueblo gris en primer plano */}
			<Houses y={1500} s={1.3} seed="fw" color="#2b3133" />
			<rect x={0} y={1500} width={1080} height={420} fill="#181c1d" />
		</Stage>
	);
};

// ---------- Mapa: dos íconos por región, luego cuatro (x2) ----------
export const MapIcons: React.FC<SceneProps & {readonly split?: boolean}> = ({dur, split = false}) => {
	const f = useCurrentFrame();
	const sp = split ? lerp(f, [8, 20], [0, 1], ease) : 0;
	const flash = split ? lerp(f, [6, 10, 22], [0, 0.7, 0]) : 0;
	const pulse = 1 + 0.15 * Math.sin(f * 0.6);
	return (
		<Camera dur={dur} origin={[540, 960]} scale={split ? [1.05, 1.12] : [1, 1.05]}>
			<Stage bg={C.deep}>
				<MapBg />
				<MapBase lines={0.3} fillFor={split ? (i) => (sp > 0.1 ? (i % 2 ? '#6a3a40' : '#5d3438') : '#596163') : undefined}>
					{REGIONS.map((r, i) => {
						const [x, y] = r.c;
						const icons = split
							? [
									[x - 24 - sp * 10, y - sp * 26],
									[x + 24 + sp * 10, y - sp * 26],
									[x - 24 - sp * 10, y + sp * 26],
									[x + 24 + sp * 10, y + sp * 26],
								]
							: [
									[x - 24, y],
									[x + 24, y],
								];
						return (
							<g key={i}>
								{icons.map(([ix, iy], k) => (
									<MapIcon key={k} x={ix} y={iy} s={0.85 * pulse} color={split && sp > 0.5 ? '#ffd9d9' : C.white} />
								))}
							</g>
						);
					})}
				</MapBase>
				<rect x={0} y={0} width={1080} height={1920} fill={C.red} opacity={flash} />
			</Stage>
		</Camera>
	);
};
