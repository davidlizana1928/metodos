import React from 'react';
import {AbsoluteFill, Easing, interpolate, random, useCurrentFrame} from 'remotion';

// Tamaño del video: vertical, para TikTok / Reels.
export const W = 1080;
export const H = 1920;

// Paleta: bruma verde azulada con acentos mostaza y carmesí.
export const C = {
	night: '#071216',
	deep: '#0c1d22',
	teal: '#1d4248',
	tealMid: '#2f6066',
	tealLight: '#7fb0a8',
	haze: '#a9c9bf',
	mustard: '#d9a63a',
	mustardDark: '#8f6420',
	crimson: '#a3243b',
	crimsonDark: '#5a1222',
	gold: '#f2c14e',
	goldLight: '#ffe7a3',
	gray: '#6b7478',
	grayDark: '#3a4245',
	coal: '#15181a',
	skin: '#b98764',
	hair: '#1b1512',
	white: '#fff6e3',
	orange: '#f07a2a',
	red: '#e8323c',
};

export const clampOpts = {
	extrapolateLeft: 'clamp',
	extrapolateRight: 'clamp',
} as const;

export const ease = Easing.bezier(0.16, 1, 0.3, 1);
export const inOut = Easing.bezier(0.65, 0, 0.35, 1);
export const easeIn = Easing.bezier(0.7, 0, 0.84, 0);

// interpolate() con límites, para no repetir opciones en cada escena.
export const lerp = (
	f: number,
	input: number[],
	output: number[],
	easing: (t: number) => number = (t) => t,
) => interpolate(f, input, output, {...clampOpts, easing});

const mod = (a: number, b: number) => ((a % b) + b) % b;

// Lienzo SVG de pantalla completa: todas las escenas dibujan aquí.
export const Stage: React.FC<{
	readonly children: React.ReactNode;
	readonly bg?: string;
}> = ({children, bg}) => (
	<AbsoluteFill style={{background: bg}}>
		<svg
			width={W}
			height={H}
			viewBox={`0 0 ${W} ${H}`}
			style={{position: 'absolute', inset: 0}}
		>
			<defs>
				<filter id="glow" x="-50%" y="-50%" width="200%" height="200%">
					<feGaussianBlur stdDeviation="8" result="b" />
					<feMerge>
						<feMergeNode in="b" />
						<feMergeNode in="SourceGraphic" />
					</feMerge>
				</filter>
				<filter id="bigGlow" x="-50%" y="-50%" width="200%" height="200%">
					<feGaussianBlur stdDeviation="30" result="b" />
					<feMerge>
						<feMergeNode in="b" />
						<feMergeNode in="SourceGraphic" />
					</feMerge>
				</filter>
				<filter id="soft">
					<feGaussianBlur stdDeviation="18" />
				</filter>
				<filter id="blur4">
					<feGaussianBlur stdDeviation="4" />
				</filter>
				{/* Bordes irregulares, como pinceladas. */}
				<filter id="paint" x="-5%" y="-5%" width="110%" height="110%">
					<feTurbulence
						type="fractalNoise"
						baseFrequency="0.018"
						numOctaves="3"
						seed="4"
					/>
					<feDisplacementMap in="SourceGraphic" scale="14" />
				</filter>
				<radialGradient id="warmGlow">
					<stop offset="0%" stopColor={C.goldLight} stopOpacity="0.9" />
					<stop offset="100%" stopColor={C.gold} stopOpacity="0" />
				</radialGradient>
				<radialGradient id="whiteGlow">
					<stop offset="0%" stopColor="#ffffff" stopOpacity="1" />
					<stop offset="100%" stopColor="#ffffff" stopOpacity="0" />
				</radialGradient>
				<radialGradient id="redGlow">
					<stop offset="0%" stopColor={C.red} stopOpacity="0.9" />
					<stop offset="100%" stopColor={C.red} stopOpacity="0" />
				</radialGradient>
				<radialGradient id="orangeGlow">
					<stop offset="0%" stopColor={C.orange} stopOpacity="0.9" />
					<stop offset="100%" stopColor={C.orange} stopOpacity="0" />
				</radialGradient>
			</defs>
			{children}
		</svg>
	</AbsoluteFill>
);

// Fondo degradado vertical.
export const SkyRect: React.FC<{
	readonly id: string;
	readonly stops: [number, string][];
	readonly x?: number;
	readonly y?: number;
	readonly w?: number;
	readonly h?: number;
}> = ({id, stops, x = 0, y = 0, w = W, h = H}) => (
	<>
		<defs>
			<linearGradient id={id} x1="0" y1="0" x2="0" y2="1">
				{stops.map(([o, c]) => (
					<stop key={o} offset={o} stopColor={c} />
				))}
			</linearGradient>
		</defs>
		<rect x={x} y={y} width={w} height={h} fill={`url(#${id})`} />
	</>
);

// Movimiento de cámara: acerca la imagen hacia un punto (ox, oy).
export const Camera: React.FC<{
	readonly dur: number;
	readonly origin: [number, number];
	readonly scale: [number, number];
	readonly shift?: [number, number, number, number];
	readonly easing?: (t: number) => number;
	readonly children: React.ReactNode;
}> = ({dur, origin, scale, shift = [0, 0, 0, 0], easing = inOut, children}) => {
	const f = useCurrentFrame();
	const t = lerp(f, [0, dur], [0, 1], easing);
	const s = scale[0] + (scale[1] - scale[0]) * t;
	const x = shift[0] + (shift[2] - shift[0]) * t;
	const y = shift[1] + (shift[3] - shift[1]) * t;
	return (
		<AbsoluteFill
			style={{
				transformOrigin: `${origin[0]}px ${origin[1]}px`,
				scale: String(s),
				translate: `${x}px ${y}px`,
			}}
		>
			{children}
		</AbsoluteFill>
	);
};

// Partículas de polvo flotando (dentro de una caja).
export const Dust: React.FC<{
	readonly n: number;
	readonly seed: string;
	readonly color?: string;
	readonly size?: [number, number];
	readonly vx?: number;
	readonly vy?: number;
	readonly opacity?: number;
	readonly box?: [number, number, number, number];
	readonly glow?: boolean;
}> = ({
	n,
	seed,
	color = C.goldLight,
	size = [1.5, 4],
	vx = 0.2,
	vy = -0.4,
	opacity = 0.8,
	box = [0, 0, W, H],
	glow = true,
}) => {
	const f = useCurrentFrame();
	const [bx, by, bw, bh] = box;
	return (
		<g filter={glow ? 'url(#glow)' : undefined}>
			{new Array(n).fill(0).map((_, i) => {
				const r1 = random(`${seed}-x-${i}`);
				const r2 = random(`${seed}-y-${i}`);
				const r3 = random(`${seed}-s-${i}`);
				const sp = 0.5 + r3;
				const x = bx + mod(r1 * bw + vx * sp * f + Math.sin(f * 0.04 + i) * 14, bw);
				const y = by + mod(r2 * bh + vy * sp * f, bh);
				const o = opacity * (0.45 + 0.55 * Math.abs(Math.sin(f * 0.07 * sp + i)));
				return (
					<circle
						key={i}
						cx={x}
						cy={y}
						r={size[0] + (size[1] - size[0]) * r3}
						fill={color}
						opacity={o}
					/>
				);
			})}
		</g>
	);
};

// Chispas que salen de un punto.
export const Sparks: React.FC<{
	readonly x: number;
	readonly y: number;
	readonly n: number;
	readonly seed: string;
	readonly color?: string;
	readonly dir?: number;
	readonly spread?: number;
	readonly dist?: number;
	readonly life?: number;
	readonly gravity?: number;
	readonly size?: number;
	readonly start?: number;
}> = ({
	x,
	y,
	n,
	seed,
	color = C.gold,
	dir = -Math.PI / 2,
	spread = 1.2,
	dist = 120,
	life = 24,
	gravity = 40,
	size = 3,
	start = 0,
}) => {
	const f = useCurrentFrame() - start;
	if (f < 0) return null;
	return (
		<g filter="url(#glow)">
			{new Array(n).fill(0).map((_, i) => {
				const off = random(`${seed}-o-${i}`) * life * 0.6;
				// Cada chispa nace en un momento distinto y se repite cada "life".
				if (f < off) return null;
				const t = mod(f - off, life) / life;
				const a = dir + (random(`${seed}-a-${i}`) - 0.5) * spread;
				const d = dist * (0.4 + 0.6 * random(`${seed}-d-${i}`)) * t;
				return (
					<circle
						key={i}
						cx={x + Math.cos(a) * d}
						cy={y + Math.sin(a) * d + gravity * t * t}
						r={size * (1 - t * 0.6)}
						fill={color}
						opacity={1 - t}
					/>
				);
			})}
		</g>
	);
};

// Brasas que suben por toda una zona.
export const Embers: React.FC<{
	readonly n: number;
	readonly seed: string;
	readonly box?: [number, number, number, number];
	readonly color?: string;
	readonly speed?: number;
}> = ({n, seed, box = [0, 0, W, H], color = C.orange, speed = 3}) => {
	const f = useCurrentFrame();
	const [bx, by, bw, bh] = box;
	return (
		<g filter="url(#glow)">
			{new Array(n).fill(0).map((_, i) => {
				const r1 = random(`${seed}-x-${i}`);
				const r2 = random(`${seed}-y-${i}`);
				const sp = speed * (0.5 + random(`${seed}-s-${i}`));
				const y = by + mod(r2 * bh - sp * f, bh);
				const x = bx + r1 * bw + Math.sin(f * 0.06 + i * 2) * 18;
				const fade = Math.min(1, (y - by) / (bh * 0.3));
				return (
					<circle
						key={i}
						cx={x}
						cy={y}
						r={2 + 3 * random(`${seed}-r-${i}`)}
						fill={i % 3 === 0 ? C.gold : color}
						opacity={fade * (0.6 + 0.4 * Math.sin(f * 0.3 + i))}
					/>
				);
			})}
		</g>
	);
};

// Silueta pequeña de una persona adulta, vista de espaldas.
// (x, y) es el punto entre los pies. h es la altura en píxeles.
export const Figure: React.FC<{
	readonly x: number;
	readonly y: number;
	readonly h: number;
	readonly color?: string;
	readonly shirt?: string;
	readonly hair?: 'short' | 'long';
	readonly dress?: string[];
	readonly walk?: number;
	readonly arms?: 'down' | 'open' | 'point' | 'clap';
	readonly armPhase?: number;
	readonly rim?: string;
	readonly headTilt?: number;
	readonly opacity?: number;
}> = ({
	x,
	y,
	h,
	color = C.coal,
	shirt,
	hair = 'short',
	dress,
	walk,
	arms = 'down',
	armPhase = 0,
	rim,
	headTilt = 0,
	opacity = 1,
}) => {
	const s = h / 260;
	const swing = walk === undefined ? 0 : Math.sin(walk) * 22;
	const body = shirt ?? color;
	let la = 8;
	let ra = -8;
	if (arms === 'open') {
		la = 85;
		ra = -85;
	} else if (arms === 'point') {
		la = 8;
		ra = -135;
	} else if (arms === 'clap') {
		const c = (Math.sin(armPhase) + 1) / 2;
		la = 40 + c * 25;
		ra = -40 - c * 25;
	} else if (walk !== undefined) {
		la = 8 - swing * 0.8;
		ra = -8 - swing * 0.8;
	}
	const stroke = rim ? {stroke: rim, strokeWidth: 2.5 / s} : {};
	return (
		<g transform={`translate(${x - 50 * s} ${y - 260 * s}) scale(${s})`} opacity={opacity}>
			{/* piernas */}
			<rect x={34} y={135} width={14} height={122} rx={6} fill={color} transform={`rotate(${swing} 41 140)`} {...stroke} />
			<rect x={52} y={135} width={14} height={122} rx={6} fill={color} transform={`rotate(${-swing} 59 140)`} {...stroke} />
			{/* brazos */}
			<rect x={22} y={56} width={12} height={78} rx={6} fill={body} transform={`rotate(${la} 28 62)`} {...stroke} />
			<rect x={66} y={56} width={12} height={78} rx={6} fill={body} transform={`rotate(${ra} 72 62)`} {...stroke} />
			{/* torso */}
			<path d="M28 56 Q50 44 72 56 L76 142 L24 142 Z" fill={body} {...stroke} />
			{dress ? (
				<g>
					<path d="M27 112 L73 112 L88 205 L12 205 Z" fill={dress[0]} {...stroke} />
					{dress.slice(1).map((c, i) => (
						<rect
							key={c + i}
							x={18 + ((i * 23) % 56)}
							y={122 + ((i * 31) % 70)}
							width={16}
							height={16}
							fill={c}
							opacity={0.9}
						/>
					))}
				</g>
			) : null}
			{/* cabeza y pelo */}
			<g transform={`rotate(${headTilt} 50 50)`}>
				<rect x={43} y={36} width={14} height={16} fill={color} />
				<circle cx={50} cy={26} r={19} fill={C.hair} {...stroke} />
				{hair === 'long'
					? [0, 1, 2, 3, 4, 5, 6, 7].map((i) => (
							<circle
								key={i}
								cx={34 + (i % 2) * 32 + Math.sin(i) * 3}
								cy={22 + Math.floor(i / 2) * 15}
								r={11}
								fill={C.hair}
							/>
						))
					: null}
			</g>
		</g>
	);
};

// El Espectador: hombre adulto, pelo oscuro corto, barba ligera,
// chaqueta con capucha mostaza. Siempre de espaldas o de perfil.
// (x, y) = centro de la base del torso. w = ancho.
export const Spectator: React.FC<{
	readonly x: number;
	readonly y: number;
	readonly w: number;
	readonly turn?: number;
	readonly rim?: string;
}> = ({x, y, w, turn = 0, rim = C.haze}) => {
	const s = w / 400;
	const hx = turn * 16;
	return (
		<g transform={`translate(${x - 200 * s} ${y - 520 * s}) scale(${s})`}>
			<defs>
				<linearGradient id="hoodie" x1="0" y1="0" x2="1" y2="1">
					<stop offset="0%" stopColor={C.mustard} />
					<stop offset="100%" stopColor={C.mustardDark} />
				</linearGradient>
			</defs>
			{/* torso con chaqueta */}
			<path
				d="M30 520 C34 410 80 338 200 326 C320 338 366 410 370 520 Z"
				fill="url(#hoodie)"
				stroke={rim}
				strokeOpacity={0.5}
				strokeWidth={4}
			/>
			{/* costura central de la espalda */}
			<path d="M200 380 L200 520" stroke={C.mustardDark} strokeWidth={6} opacity={0.5} />
			{/* cuello */}
			<rect x={172} y={262} width={56} height={74} rx={18} fill={C.skin} />
			<path d="M172 300 Q200 316 228 300 L228 336 L172 336 Z" fill="#8a5f44" />
			{/* capucha recogida detrás del cuello */}
			<path
				d="M112 352 C112 292 288 292 288 352 C268 384 132 384 112 352 Z"
				fill={C.mustard}
				stroke={C.mustardDark}
				strokeWidth={5}
			/>
			{/* cabeza */}
			<g transform={`translate(${hx} 0) rotate(${turn * 6} 200 200)`}>
				{/* perfil: nariz y barba aparecen al girar */}
				<g opacity={turn}>
					<path
						d="M262 168 L292 214 L264 222 Z"
						fill={C.skin}
					/>
					<path
						d="M150 236 C170 292 252 300 270 240 L262 222 C240 270 180 270 160 226 Z"
						fill="#2a201b"
					/>
				</g>
				<ellipse cx={200} cy={196} rx={70} ry={84} fill={C.skin} />
				{/* orejas */}
				<ellipse cx={128} cy={204} rx={12} ry={22} fill="#a87656" />
				<ellipse cx={272 - turn * 10} cy={204} rx={12} ry={22} fill="#a87656" opacity={1 - turn * 0.6} />
				{/* pelo corto oscuro */}
				<path
					d="M126 196 C120 120 170 104 204 106 C250 108 282 136 274 200 C268 236 254 252 236 258 C214 262 186 262 164 258 C144 252 130 232 126 196 Z"
					fill={C.hair}
				/>
				{/* barba ligera en la mandíbula */}
				<path d="M140 226 C150 260 172 272 200 274 C228 272 250 260 260 226" stroke="#2a201b" strokeWidth={10} fill="none" opacity={0.7} />
				{/* luz de borde */}
				<path d="M126 196 C120 120 170 104 204 106" stroke={rim} strokeWidth={4} fill="none" opacity={0.6} />
			</g>
		</g>
	);
};

// Urna de vidrio alta con papeles doblados.
// (x, y) = centro de la base. h = altura.
export const Urn: React.FC<{
	readonly x: number;
	readonly y: number;
	readonly h: number;
	readonly draw?: number;
	readonly glass?: number;
	readonly agitation?: number;
	readonly stroke?: string;
	readonly seed?: string;
}> = ({x, y, h, draw = 1, glass = 1, agitation = 1, stroke = C.haze, seed = 'urn'}) => {
	const f = useCurrentFrame();
	const s = h / 420;
	const outline =
		'M70 400 L230 400 L230 380 L214 372 C246 300 250 160 226 70 L240 54 L240 36 L60 36 L60 54 L74 70 C50 160 54 300 86 372 L70 380 Z';
	return (
		<g transform={`translate(${x - 150 * s} ${y - 420 * s}) scale(${s})`}>
			<path d={outline} fill={C.tealLight} opacity={0.18 * glass} />
			{/* papeles */}
			<g opacity={glass}>
				{new Array(26).fill(0).map((_, i) => {
					const r1 = random(`${seed}-${i}-a`);
					const r2 = random(`${seed}-${i}-b`);
					const px = 90 + r1 * 120 + Math.sin(f * 0.3 + i) * 6 * agitation;
					const py = 210 + r2 * 160 + Math.cos(f * 0.25 + i * 2) * 8 * agitation;
					return (
						<rect
							key={i}
							x={px}
							y={py}
							width={22}
							height={14}
							fill={i % 5 === 0 ? '#e8dcc0' : C.white}
							transform={`rotate(${(r1 - 0.5) * 80 + Math.sin(f * 0.2 + i) * 20 * agitation} ${px + 11} ${py + 7})`}
						/>
					);
				})}
			</g>
			{/* reflejo del vidrio */}
			<path d="M96 90 C80 180 82 280 104 350" stroke="#ffffff" strokeWidth={8} fill="none" opacity={0.35 * glass} />
			<path
				d={outline}
				fill="none"
				stroke={stroke}
				strokeWidth={6}
				pathLength={1}
				strokeDasharray="1 1"
				strokeDashoffset={1 - draw}
			/>
		</g>
	);
};
