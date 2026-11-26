import React from 'react';
import {useCurrentFrame} from 'remotion';
import {C, lerp} from './base';

// Geometría del mapa: una capital al centro y regiones alrededor.
export const MAP = {cx: 540, cy: 960, rin: 120, n: 12};

const outerR = (a: number) =>
	400 + 45 * Math.sin(3 * a + 1) + 28 * Math.sin(5 * a + 2) + 14 * Math.sin(9 * a);

const pt = (a: number, r: number): [number, number] => [
	MAP.cx + Math.cos(a) * r,
	MAP.cy + Math.sin(a) * r * 1.3,
];

const edgeAngle = (i: number, u: number) =>
	(i / MAP.n) * Math.PI * 2 + 0.09 * Math.sin(u * 5 + i * 1.7) - Math.PI / 2;

const regionPath = (i: number) => {
	const pts: [number, number][] = [];
	const steps = 10;
	for (let k = 0; k <= steps; k++) {
		const u = k / steps;
		const a = edgeAngle(i, u);
		pts.push(pt(a, MAP.rin + u * (outerR(a) - MAP.rin)));
	}
	const a0 = edgeAngle(i, 1);
	const a1 = edgeAngle(i + 1, 1);
	for (let k = 1; k < steps; k++) {
		const a = a0 + ((a1 - a0) * k) / steps;
		pts.push(pt(a, outerR(a)));
	}
	for (let k = steps; k >= 0; k--) {
		const u = k / steps;
		const a = edgeAngle(i + 1, u);
		pts.push(pt(a, MAP.rin + u * (outerR(a) - MAP.rin)));
	}
	return 'M' + pts.map((p) => p.map((v) => v.toFixed(1)).join(' ')).join(' L') + ' Z';
};

export const REGIONS = new Array(MAP.n).fill(0).map((_, i) => {
	const mid = edgeAngle(i, 0.6) + Math.PI / MAP.n;
	const r = (MAP.rin + outerR(mid)) * 0.6;
	return {d: regionPath(i), c: pt(mid, r), angle: mid};
});

const GRAYS = ['#596163', '#646b6c', '#4f5759', '#6d7372'];

// Mapa base. fillFor(i) permite pintar cada región de otro color.
export const MapBase: React.FC<{
	readonly fillFor?: (i: number) => string;
	readonly glowFor?: (i: number) => number;
	readonly capitalGlow?: number;
	readonly lines?: number;
	readonly children?: React.ReactNode;
}> = ({fillFor, glowFor, capitalGlow = 1, lines = 0.5, children}) => {
	const f = useCurrentFrame();
	return (
		<g>
			{/* sombra del país */}
			<g filter="url(#paint)">
				<path
					d={REGIONS.map((r) => r.d).join(' ')}
					fill="#000"
					opacity={0.45}
					transform="translate(14 22)"
				/>
				{REGIONS.map((r, i) => (
					<path
						key={i}
						d={r.d}
						fill={fillFor ? fillFor(i) : GRAYS[i % GRAYS.length]}
						stroke="#2b3133"
						strokeWidth={5}
					/>
				))}
			</g>
			{glowFor
				? REGIONS.map((r, i) => (
						<path
							key={i}
							d={r.d}
							fill={C.orange}
							opacity={glowFor(i) * 0.55}
							filter="url(#glow)"
						/>
					))
				: null}
			{/* caminos desde la capital */}
			{REGIONS.map((r, i) => (
				<line
					key={i}
					x1={MAP.cx}
					y1={MAP.cy}
					x2={r.c[0]}
					y2={r.c[1]}
					stroke={C.gold}
					strokeWidth={3}
					strokeDasharray="10 10"
					opacity={lines}
				/>
			))}
			{/* capital dorada y brillante */}
			<circle
				cx={MAP.cx}
				cy={MAP.cy}
				r={260}
				fill="url(#warmGlow)"
				opacity={0.55 * capitalGlow * (0.85 + 0.15 * Math.sin(f * 0.2))}
			/>
			<g filter="url(#paint)">
				<circle cx={MAP.cx} cy={MAP.cy} r={MAP.rin - 8} fill={C.gold} stroke="#a77a1c" strokeWidth={8} />
				{[0, 1, 2, 3, 4, 5].map((k) => (
					<rect
						key={k}
						x={MAP.cx - 62 + k * 22}
						y={MAP.cy - 30 - (k % 3) * 22}
						width={16}
						height={60 + (k % 3) * 22}
						fill={C.goldLight}
						stroke="#a77a1c"
						strokeWidth={3}
					/>
				))}
			</g>
			{children}
		</g>
	);
};

// Icono de silueta para el mapa.
export const MapIcon: React.FC<{
	readonly x: number;
	readonly y: number;
	readonly s?: number;
	readonly color?: string;
}> = ({x, y, s = 1, color = C.white}) => (
	<g transform={`translate(${x} ${y}) scale(${s})`} filter="url(#glow)">
		<circle cx={0} cy={-16} r={9} fill={color} />
		<path d="M-14 14 C-14 -4 14 -4 14 14 Z" fill={color} />
	</g>
);

export const regionLerp = (f: number, i: number, start: number, step: number, len: number) =>
	lerp(f, [start + i * step, start + i * step + len], [0, 1]);
