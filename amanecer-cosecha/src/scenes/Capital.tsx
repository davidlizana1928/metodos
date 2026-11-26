import React from 'react';
import {random, useCurrentFrame} from 'remotion';
import {C, Camera, Dust, Embers, Figure, SkyRect, Sparks, Spectator, Stage, Urn, ease, easeIn, inOut, lerp} from '../lib/base';
import {MAP, MapBase, REGIONS} from '../lib/map';

type SceneProps = {readonly dur: number};

// Multitud de siluetas adultas (cabezas y hombros), vista de espaldas.
const Crowd: React.FC<{
	readonly y: number;
	readonly rows: number;
	readonly seed: string;
	readonly turn?: number;
	readonly towardX?: number;
	readonly rim?: string;
	readonly gap?: number;
}> = ({y, rows, seed, turn = 0, towardX = 540, rim, gap}) => (
	<g>
		{new Array(rows).fill(0).map((_, r) => {
			const s = 0.7 + r * 0.35;
			const step = 70 * s;
			const n = Math.ceil(1200 / step);
			return (
				<g key={r}>
					{new Array(n).fill(0).map((__, i) => {
						const x = i * step - 40 + (r % 2) * step * 0.5 + random(`${seed}-${r}-${i}`) * 14;
						if (gap !== undefined && Math.abs(x - gap) < 90 && r === rows - 2) return null;
						const yy = y + r * 70 * s;
						const lean = turn * Math.sign(towardX - x) * 8;
						const tone = r === rows - 1 ? '#121617' : '#1d2224';
						return (
							<g key={i} transform={`rotate(${lean} ${x} ${yy + 60 * s})`}>
								<rect x={x - 30 * s} y={yy + 14 * s} width={60 * s} height={140 * s} rx={22 * s} fill={tone} />
								<circle cx={x + lean * 1.5} cy={yy} r={20 * s} fill={tone} stroke={rim} strokeWidth={rim ? 2 : 0} strokeOpacity={0.6} />
							</g>
						);
					})}
				</g>
			);
		})}
	</g>
);

// ---------- Mano enguantada saca un papel de la urna ----------
export const Reaping: React.FC<SceneProps> = ({dur}) => {
	const f = useCurrentFrame();
	const hand = lerp(f, [0, 0.25 * dur, 0.5 * dur], [-300, 0, -260], inOut);
	const paper = f > 0.25 * dur;
	return (
		<Camera dur={dur} origin={[540, 960]} scale={[1.1, 1.1]} shift={[0, 200, 0, -700]} easing={inOut}>
			<Stage bg="#5d6668">
				<SkyRect id="rp-sky" stops={[[0, '#6f797a'], [1, '#4c5557']]} />
				{/* escenario */}
				<rect x={60} y={260} width={960} height={40} fill="#2b3133" />
				<rect x={100} y={300} width={20} height={600} fill="#2b3133" />
				<rect x={960} y={300} width={20} height={600} fill="#2b3133" />
				<rect x={40} y={880} width={1000} height={80} fill="#3a4143" />
				<Urn x={540} y={880} h={520} seed="reap" agitation={0.4} />
				{/* mano con guante gris */}
				<g transform={`translate(560 ${420 + hand})`}>
					<rect x={-28} y={-500} width={56} height={460} rx={20} fill="#2c3234" />
					<path d="M-38 -60 L38 -60 L44 10 C44 40 -44 40 -44 10 Z" fill="#555d60" />
					{paper ? <rect x={-30} y={30} width={60} height={36} fill={C.white} transform="rotate(-8)" /> : null}
				</g>
				{/* multitud en silencio */}
				<rect x={0} y={960} width={1080} height={1700} fill="#4a5254" />
				<Crowd y={1100} rows={9} seed="reap-crowd" />
				<Dust n={40} seed="reap-dust" color="#d6dbd9" vx={0.6} vy={-0.2} opacity={0.35} glow={false} box={[0, 0, 1080, 2600]} />
			</Stage>
		</Camera>
	);
};

// ---------- El papel no tiene su nombre: alivio ----------
export const Relief: React.FC<SceneProps> = ({dur}) => {
	const f = useCurrentFrame();
	const exhale = lerp(f, [0.3 * dur, 0.8 * dur], [0, 1], ease);
	return (
		<Camera dur={dur} origin={[540, 1300]} scale={[1.15, 1.05]}>
			<Stage bg="#4a5254">
				<SkyRect id="rl-sky" stops={[[0, '#5d6668'], [1, '#3b4244']]} />
				{/* papel desplegado en la pantalla del escenario: garabatos ilegibles */}
				<g transform="translate(540 470) rotate(-3)">
					<rect x={-260} y={-150} width={520} height={300} fill={C.white} />
					{[0, 1, 2].map((k) => (
						<path key={k} d={`M-200 ${-70 + k * 60} q40 -20 80 0 t80 0 t80 0 t80 0`} stroke="#5a5a5a" strokeWidth={8} fill="none" opacity={0.6} />
					))}
				</g>
				<Crowd y={980} rows={6} seed="rl-crowd" gap={540} />
				{/* el joven, de espaldas: los hombros bajan con alivio */}
				<Figure x={540} y={1700 + exhale * 10} h={560} color="#171b1c" shirt="#7d8586" rim="#e2e7e4" />
				<Crowd y={1650} rows={2} seed="rl-front" gap={540} />
				<rect x={0} y={0} width={1080} height={1920} fill={C.gold} opacity={exhale * 0.08} />
			</Stage>
		</Camera>
	);
};

// ---------- Ella avanza hacia los guardias ----------
const Guards: React.FC<{readonly y: number; readonly h: number; readonly shine: number}> = ({y, h, shine}) => (
	<g>
		{new Array(7).fill(0).map((_, i) => {
			const x = 80 + i * 155;
			const s = h / 260;
			const sh = Math.max(0, 1 - Math.abs(shine * 9 - i) / 1.2);
			return (
				<g key={i}>
					<Figure x={x} y={y} h={h} color="#23292b" shirt="#30383a" />
					{/* casco con visera (sin rostro) */}
					<ellipse cx={x} cy={y - h + 26 * s} rx={24 * s} ry={22 * s} fill="#3a4346" />
					<rect x={x - 20 * s} y={y - h + 22 * s} width={40 * s} height={14 * s} rx={6} fill="#0e1314" />
					<rect x={x - 20 * s} y={y - h + 22 * s} width={40 * s} height={6 * s} rx={3} fill="#e6f0ee" opacity={sh} filter="url(#glow)" />
				</g>
			);
		})}
	</g>
);

const PATCH = ['#7a4b6a', C.mustard, C.crimson, '#3f7c8a', '#6f9a55', '#c46a3a'];

export const GuardsScene: React.FC<SceneProps> = ({dur}) => {
	const f = useCurrentFrame();
	const walk = lerp(f, [0, dur], [0, 1]);
	return (
		<Camera dur={dur} origin={[540, 1100]} scale={[1, 1.08]}>
			<Stage bg="#4a5254">
				<SkyRect id="gd-sky" stops={[[0, '#5d6668'], [0.6, '#4a5254'], [1, '#353b3d']]} />
				<rect x={0} y={1080} width={1080} height={840} fill="#3a4143" />
				<Guards y={1150} h={320} shine={lerp(f, [0, dur], [0, 1])} />
				<Figure x={540} y={1850 - walk * 420} h={520 - walk * 160} color="#2a2422" hair="long" dress={PATCH} walk={f * 0.3} />
			</Stage>
		</Camera>
	);
};

// ---------- Cámara lenta: él se interpone con los brazos abiertos ----------
export const SlowMoRun: React.FC<SceneProps> = ({dur}) => {
	const f = useCurrentFrame();
	const run = lerp(f, [0, 0.75 * dur], [0, 1], ease);
	const x = 140 + run * 400;
	return (
		<Camera dur={dur} origin={[540, 1200]} scale={[1.05, 1.12]}>
			<Stage bg="#4a5254">
				<SkyRect id="sm-sky" stops={[[0, '#5d6668'], [1, '#353b3d']]} />
				<rect x={0} y={1080} width={1080} height={840} fill="#3a4143" />
				<Guards y={1150} h={320} shine={0.5} />
				<Figure x={540} y={1700} h={360} color="#2a2422" hair="long" dress={PATCH} />
				<Figure x={x} y={1500} h={400} color="#171b1c" shirt="#7d8586" walk={run < 1 ? f * 0.12 : undefined} arms={run > 0.6 ? 'open' : 'down'} rim="#e2e7e4" />
				{/* polvo que se levanta a cada paso */}
				{[0.15, 0.35, 0.55, 0.75].map((p, k) => {
					const at = p * dur;
					if (f < at) return null;
					const t = lerp(f, [at, at + 30], [0, 1], ease);
					const px = 140 + lerp(at, [0, 0.75 * dur], [0, 1], ease) * 400;
					return (
						<g key={k} opacity={1 - t} filter="url(#soft)">
							<circle cx={px - 30} cy={1500 - t * 40} r={30 + t * 60} fill="#b8bdb9" />
							<circle cx={px + 30} cy={1500 - t * 30} r={24 + t * 50} fill="#b8bdb9" />
						</g>
					);
				})}
			</Stage>
		</Camera>
	);
};

// ---------- Foco blanco: la multitud se gira ----------
export const Spotlight: React.FC<SceneProps> = ({dur}) => {
	const f = useCurrentFrame();
	const on = lerp(f, [0, 6], [0, 1]);
	const turn = lerp(f, [0.25 * dur, 0.8 * dur], [0, 1], ease);
	return (
		<Camera dur={dur} origin={[540, 1100]} scale={[1, 1.12]}>
			<Stage bg="#0a0f10">
				<polygon points="470,-20 610,-20 760,1500 320,1500" fill="#ffffff" opacity={0.18 * on} filter="url(#blur4)" />
				<ellipse cx={540} cy={1480} rx={240} ry={60} fill="#ffffff" opacity={0.35 * on} />
				<Figure x={540} y={1480} h={420} color="#171b1c" shirt="#9aa2a3" arms="open" rim="#ffffff" />
				<Crowd y={1450} rows={5} seed="sp-crowd" turn={turn} rim="#ffffff" gap={540} />
			</Stage>
		</Camera>
	);
};

// ---------- Tren nocturno hacia la capital dorada ----------
export const Train: React.FC<SceneProps> = ({dur}) => {
	const f = useCurrentFrame();
	const tx = lerp(f, [0, dur], [-1400, 300]);
	return (
		<Stage bg="#071216">
			<SkyRect id="tr-sky" stops={[[0, '#061014'], [0.7, '#132a2e'], [1, '#2b2a1c']]} />
			<Dust n={70} seed="stars" color="#ffffff" vx={0} vy={0} size={[1, 2]} opacity={0.7} box={[0, 0, 1080, 900]} />
			<ellipse cx={980} cy={1050} rx={360} ry={140} fill="url(#warmGlow)" />
			{[0, 1, 2, 3, 4].map((k) => (
				<rect key={k} x={880 + k * 36} y={1000 - (k % 3) * 50} width={24} height={120 + (k % 3) * 50} fill={C.gold} opacity={0.85} />
			))}
			<path d="M-50 1150 C300 1000 600 1100 1130 1080 L1130 1920 L-50 1920 Z" fill="#0c1a1c" />
			<rect x={-50} y={1290} width={1200} height={8} fill="#2a3436" />
			<g transform={`translate(${tx} 0)`}>
				{new Array(6).fill(0).map((_, c) => (
					<g key={c} transform={`translate(${c * 230} 0)`}>
						<rect x={0} y={1180} width={220} height={110} rx={14} fill="#11191b" />
						{[0, 1, 2, 3].map((w) => (
							<rect key={w} x={18 + w * 50} y={1200} width={36} height={34} fill={C.goldLight} filter="url(#glow)" />
						))}
					</g>
				))}
				<rect x={1380} y={1160} width={180} height={130} rx={30} fill="#11191b" />
				<circle cx={1560} cy={1220} r={60} fill="url(#warmGlow)" />
			</g>
			<Embers n={18} seed="train-sparks" box={[0, 1150, 1080, 200]} speed={1} />
		</Stage>
	);
};

// ---------- Estadío: aplauso lento con burla ----------
const Stadium: React.FC<{readonly clap?: boolean; readonly target?: number; readonly lean?: number}> = ({clap = true, target = 0, lean = 0}) => {
	const f = useCurrentFrame();
	return (
		<>
			<SkyRect id="st-sky" stops={[[0, '#061014'], [1, '#1a2224']]} />
			{/* gradas llenas de luces */}
			{new Array(10).fill(0).map((_, r) =>
				new Array(24).fill(0).map((__, i) => {
					const flick = random(`st-${r}-${i}-${Math.floor(f / 4)}`) > 0.9 ? 1 : 0.35;
					return <circle key={`${r}-${i}`} cx={20 + i * 45 + (r % 2) * 22} cy={1250 + r * 60} r={6} fill={C.goldLight} opacity={flick} />;
				}),
			)}
			{/* balcón alto con el gobernante (solo silueta) */}
			<rect x={760} y={260} width={280} height={30} fill="#3b3420" />
			<rect x={760} y={290} width={280} height={180} fill="#14181a" />
			<g transform={`rotate(${lean * 14} 900 260)`}>
				<Figure x={900} y={300} h={190} color="#050708" />
			</g>
			{/* pantalla gigante con la silueta del joven aplaudiendo */}
			<rect x={70} y={560} width={760} height={560} fill="#1d2325" />
			<rect x={90} y={580} width={720} height={520} fill="#24484c" />
			<rect x={90} y={580} width={720} height={520} fill={C.haze} opacity={0.15} />
			<Figure x={450} y={1060} h={380} color="#0d1112" shirt="#7d8586" arms={clap ? 'clap' : 'down'} armPhase={f * 0.22} rim="#e2e7e4" />
			{target > 0 ? (
				<g transform={`translate(450 830) rotate(${(1 - target) * 90}) scale(${1 + (1 - target) * 2})`} opacity={target}>
					<circle r={200} fill="none" stroke={C.red} strokeWidth={10} filter="url(#glow)" />
					<circle r={150} fill="none" stroke={C.red} strokeWidth={4} strokeDasharray="20 16" />
					{[0, 90, 180, 270].map((a) => (
						<line key={a} x1={0} y1={-240} x2={0} y2={-170} stroke={C.red} strokeWidth={10} transform={`rotate(${a})`} />
					))}
				</g>
			) : null}
			{/* flashes de cámaras */}
			{new Array(14).fill(0).map((_, i) => {
				const fx = random(`flash-x-${i}`) * 1080;
				const fy = 1150 + random(`flash-y-${i}`) * 700;
				const on = (f + Math.floor(random(`flash-o-${i}`) * 40)) % 40 < 3;
				return on ? <circle key={i} cx={fx} cy={fy} r={40} fill="url(#whiteGlow)" /> : null;
			})}
		</>
	);
};

export const StadiumScene: React.FC<SceneProps> = ({dur}) => (
	<Camera dur={dur} origin={[540, 900]} scale={[1, 1.1]}>
		<Stage bg="#061014">
			<Stadium />
		</Stage>
	</Camera>
);

export const TargetLock: React.FC<SceneProps> = ({dur}) => {
	const f = useCurrentFrame();
	const lock = lerp(f, [0, 0.35 * dur], [0, 1], ease);
	const beat = 1 + 0.06 * Math.max(0, Math.sin(f * 0.7));
	return (
		<Camera dur={dur} origin={[450, 830]} scale={[1.3, 1.5 * beat]}>
			<Stage bg="#061014">
				<Stadium clap={false} target={lock} />
				<rect x={0} y={0} width={1080} height={1920} fill={C.red} opacity={0.08 * lock * Math.max(0, Math.sin(f * 0.7))} />
			</Stage>
		</Camera>
	);
};

// ---------- Decenas de lentes rojos sobre la capital ----------
export const CameraLenses: React.FC<SceneProps> = ({dur}) => {
	const f = useCurrentFrame();
	const towers = [
		[60, 700, 150],
		[230, 520, 170],
		[420, 360, 200],
		[640, 480, 170],
		[830, 620, 190],
	];
	return (
		<Camera dur={dur} origin={[540, 900]} scale={[1, 1.12]}>
			<Stage bg="#061014">
				<SkyRect id="cl-sky" stops={[[0, '#050c0f'], [1, '#2a2618']]} />
				{towers.map(([x, y, w], i) => (
					<g key={i}>
						<rect x={x} y={y} width={w} height={1920} fill="#3a311b" stroke={C.gold} strokeOpacity={0.4} strokeWidth={4} />
						{new Array(18).fill(0).map((_, k) => (
							<rect key={k} x={x + 14 + (k % 3) * (w / 3.3)} y={y + 30 + Math.floor(k / 3) * 80} width={w / 5} height={30} fill={C.gold} opacity={0.35} />
						))}
					</g>
				))}
				{/* lentes rojos que se encienden uno a uno */}
				{new Array(42).fill(0).map((_, i) => {
					const t = towers[i % towers.length];
					const lx = t[0] + 20 + random(`lens-x-${i}`) * (t[2] - 40);
					const ly = t[1] + 40 + random(`lens-y-${i}`) * 900;
					const on = lerp(f, [i * ((dur * 0.7) / 42), i * ((dur * 0.7) / 42) + 4], [0, 1]);
					return (
						<g key={i} opacity={on}>
							<circle cx={lx} cy={ly} r={26} fill="url(#redGlow)" />
							<circle cx={lx} cy={ly} r={9} fill={C.red} stroke="#ffb3b3" strokeWidth={2} />
						</g>
					);
				})}
				{/* balcón: el gobernante se inclina hacia adelante */}
				<rect x={700} y={250} width={300} height={24} fill="#5a4a22" />
				<g transform={`rotate(${lerp(f, [0.4 * dur, dur], [0, 16], ease)} 850 250)`}>
					<Figure x={850} y={260} h={200} color="#050708" />
				</g>
			</Stage>
		</Camera>
	);
};

// ---------- Manos girando un colgante de metal ----------
export const Pendant: React.FC<SceneProps> = ({dur}) => {
	const f = useCurrentFrame();
	const spin = Math.cos(f * 0.18);
	return (
		<Camera dur={dur} origin={[540, 1000]} scale={[1.05, 1.2]}>
			<Stage bg="#0a1418">
				<SkyRect id="pd-bg" stops={[[0, '#0d1e26'], [1, '#081014']]} />
				{/* cortina lujosa y fría */}
				{new Array(10).fill(0).map((_, i) => (
					<rect key={i} x={i * 110} y={0} width={70} height={1920} fill="#13303a" opacity={0.5} />
				))}
				<rect x={0} y={0} width={1080} height={1920} fill="#0a1418" opacity={0.4} />
				{/* manos */}
				<path d="M120 1500 C220 1300 380 1150 470 1080 C500 1060 520 1100 500 1130 L420 1240 C380 1320 280 1500 200 1600 Z" fill={C.skin} />
				<path d="M960 1500 C860 1300 700 1150 610 1080 C580 1060 560 1100 580 1130 L660 1240 C700 1320 800 1500 880 1600 Z" fill={C.skin} />
				<path d="M120 1500 L200 1600 L60 1700 L0 1600 Z" fill={C.mustard} />
				<path d="M960 1500 L880 1600 L1020 1700 L1080 1600 Z" fill={C.mustard} />
				{/* colgante */}
				<line x1={470} y1={1080} x2={540} y2={980} stroke="#b9c2c4" strokeWidth={4} />
				<line x1={610} y1={1080} x2={540} y2={980} stroke="#b9c2c4" strokeWidth={4} />
				<g transform={`translate(540 1060) scale(${Math.abs(spin) * 0.9 + 0.1} 1)`}>
					<circle r={64} fill={spin > 0 ? '#c9a24a' : '#8f7434'} stroke="#f2dc9a" strokeWidth={6} />
					<circle r={40} fill="none" stroke="#f2dc9a" strokeWidth={4} />
					<path d="M-24 0 L0 -26 L24 0 L0 26 Z" fill="#f2dc9a" />
				</g>
				<Sparks x={540} y={1060} n={34} seed="pendant" dist={260} life={20} spread={Math.PI * 2} gravity={60} size={4} />
			</Stage>
		</Camera>
	);
};

// ---------- La chispa dibuja el plano luminoso de una cúpula ----------
export const DomeBlueprint: React.FC<SceneProps> = ({dur}) => {
	const f = useCurrentFrame();
	const d = lerp(f, [0.1 * dur, 0.85 * dur], [0, 1], ease);
	const lines: string[] = [];
	for (let k = 1; k <= 6; k++) {
		const rx = (k / 6) * 420;
		lines.push(`M${540 - rx} 1300 A${rx} 640 0 0 1 ${540 + rx} 1300`);
	}
	for (let k = 1; k <= 5; k++) {
		const y = 1300 - k * 110;
		const rx = 420 * Math.sqrt(1 - Math.pow((1300 - y) / 640, 2));
		lines.push(`M${540 - rx} ${y} L${540 + rx} ${y}`);
	}
	lines.push('M100 1300 L980 1300', 'M540 660 L540 1300');
	const spark = lerp(f, [0, 0.2 * dur], [0, 1], ease);
	return (
		<Camera dur={dur} origin={[540, 1000]} scale={[1.1, 1]}>
			<Stage bg="#081218">
				<SkyRect id="db-bg" stops={[[0, '#081218'], [1, '#0d1e26']]} />
				<circle cx={540} cy={1400} r={60 + spark * 200} fill="url(#warmGlow)" opacity={1 - d * 0.6} />
				<g filter="url(#glow)">
					{lines.map((p, i) => (
						<path
							key={i}
							d={p}
							stroke={i % 3 === 0 ? C.gold : '#9fe3ff'}
							strokeWidth={i < 6 ? 4 : 3}
							fill="none"
							pathLength={1}
							strokeDasharray="1 1"
							strokeDashoffset={1 - lerp(d, [i * 0.04, i * 0.04 + 0.5], [0, 1])}
						/>
					))}
				</g>
				<Sparks x={540} y={1400} n={20} seed="dome" dist={200} life={22} spread={Math.PI * 2} gravity={30} />
			</Stage>
		</Camera>
	);
};

// ---------- Las líneas encienden las regiones en naranja ----------
export const MapIgnite: React.FC<SceneProps> = ({dur}) => {
	const f = useCurrentFrame();
	const lit = (i: number) => lerp(f, [10 + i * ((dur - 30) / 12), 22 + i * ((dur - 30) / 12)], [0, 1]);
	return (
		<Camera dur={dur} origin={[540, 960]} scale={[1.08, 1]}>
			<Stage bg={C.deep}>
				<SkyRect id="mi-bg" stops={[[0, '#0c1d22'], [1, '#081316']]} />
				<MapBase
					lines={0.2}
					capitalGlow={0.6}
					fillFor={(i) => (lit(i) > 0.5 ? '#c4622a' : '#4f5759')}
					glowFor={lit}
				>
					{REGIONS.map((r, i) => {
						const t = lerp(f, [i * ((dur - 30) / 12), 12 + i * ((dur - 30) / 12)], [0, 1], ease);
						return (
							<path
								key={i}
								d={`M540 -20 Q${(540 + r.c[0]) / 2} ${r.c[1] / 3} ${r.c[0]} ${r.c[1]}`}
								stroke={C.orange}
								strokeWidth={5}
								fill="none"
								filter="url(#glow)"
								pathLength={1}
								strokeDasharray="1 1"
								strokeDashoffset={1 - t}
							/>
						);
					})}
				</MapBase>
				<Embers n={30} seed="mi-embers" />
				<circle cx={MAP.cx} cy={MAP.cy} r={1} fill="none" />
			</Stage>
		</Camera>
	);
};

// ---------- El Espectador mira el mapa encendido desde la ventana ----------
export const WindowSpectator: React.FC<SceneProps> = ({dur}) => (
	<Camera dur={dur} origin={[540, 1000]} scale={[1, 1.08]}>
		<Stage bg="#081014">
			<SkyRect id="ws-bg" stops={[[0, '#0a1418'], [1, '#05090b']]} />
			{/* ventana: ciudad de noche con el mapa encendido */}
			<SkyRect id="ws-out" x={140} y={260} w={800} h={1100} stops={[[0, '#160e0a'], [1, '#3a1d10']]} />
			<g transform="translate(140 260) scale(0.74)">
				<MapBase fillFor={() => '#c4622a'} glowFor={() => 1} lines={0.3} capitalGlow={0.4} />
			</g>
			{[0, 1, 2, 3, 4, 5, 6].map((k) => (
				<rect key={k} x={150 + k * 115} y={1200 - (k % 3) * 60} width={90} height={200} fill="#0b0c0c" />
			))}
			<rect x={140} y={260} width={800} height={1100} fill="none" stroke="#1c2b30" strokeWidth={40} />
			<line x1={540} y1={260} x2={540} y2={1360} stroke="#1c2b30" strokeWidth={22} />
			<line x1={140} y1={810} x2={940} y2={810} stroke="#1c2b30" strokeWidth={22} />
			<Embers n={40} seed="ws-embers" box={[100, 300, 880, 1500]} />
			<Spectator x={540} y={1920} w={560} rim={C.orange} />
		</Stage>
	</Camera>
);

// ---------- Valle con niebla: escotillas que se abren ----------
const Valley: React.FC<{readonly open: number; readonly rise?: number; readonly chain?: number}> = ({open, rise = 0, chain = 0}) => {
	const f = useCurrentFrame();
	const n = 12;
	return (
		<>
			<SkyRect id="vl-sky" stops={[[0, '#a9c9bf'], [0.5, '#e6c79a'], [1, '#6f8f84']]} />
			<path d="M-50 900 C200 700 450 760 600 820 C800 700 950 760 1130 860 L1130 1920 L-50 1920 Z" fill="#4e6d62" filter="url(#paint)" />
			<path d="M-50 1100 C300 980 700 1040 1130 1000 L1130 1920 L-50 1920 Z" fill="#3c574e" />
			{new Array(n).fill(0).map((_, i) => {
				const a = (i / n) * Math.PI * 2;
				const x = 540 + Math.cos(a) * 360;
				const y = 1360 + Math.sin(a) * 150;
				const sc = 0.7 + (Math.sin(a) + 1) * 0.25;
				const lit = lerp(chain, [i / n, i / n + 0.1], [0, 1]);
				return (
					<g key={i} transform={`translate(${x} ${y}) scale(${sc})`}>
						<ellipse rx={60} ry={22} fill="#6f7a7c" stroke="#9aa5a6" strokeWidth={4} />
						<ellipse rx={50 * open} ry={16 * open} fill="#0b0d0e" />
						<ellipse rx={64} ry={24} fill="none" stroke="#9fe3ff" strokeWidth={6} opacity={lit} filter="url(#glow)" />
						{rise > 0 ? <Figure x={0} y={-rise * 30} h={110} color="#141819" opacity={lerp(rise, [0, 0.3], [0, 1])} /> : null}
						{open > 0.3
							? [0, 1, 2].map((k) => {
									const t = ((f * 0.9 + k * 10 + i * 3) % 30) / 30;
									return <circle key={k} cx={Math.sin(k + i) * 10} cy={-t * 140} r={18 + t * 40} fill="#f1f4f2" opacity={(1 - t) * 0.6} filter="url(#blur4)" />;
								})
							: null}
					</g>
				);
			})}
			{/* niebla */}
			<rect x={0} y={1100} width={1080} height={600} fill="#e9efec" opacity={0.18} filter="url(#soft)" />
			<Dust n={30} seed="fog" color="#ffffff" size={[30, 60]} vx={0.8} vy={0} opacity={0.12} glow={false} box={[0, 1000, 1080, 700]} />
		</>
	);
};

export const Hatches: React.FC<SceneProps> = ({dur}) => {
	const f = useCurrentFrame();
	return (
		<Camera dur={dur} origin={[540, 1300]} scale={[1.15, 1]}>
			<Stage bg="#a9c9bf">
				<Valley open={lerp(f, [0.15 * dur, 0.6 * dur], [0, 1], ease)} />
			</Stage>
		</Camera>
	);
};

export const Platforms: React.FC<SceneProps> = ({dur}) => {
	const f = useCurrentFrame();
	return (
		<Camera dur={dur} origin={[540, 1300]} scale={[1, 1.05]}>
			<Stage bg="#a9c9bf">
				<Valley open={1} rise={lerp(f, [0, 0.8 * dur], [0, 1], ease)} chain={lerp(f, [0, 0.8 * dur], [0, 1])} />
				<Spectator x={300} y={2000} w={460} rim="#ffffff" />
			</Stage>
		</Camera>
	);
};

// ---------- Lente gigante en el cielo ----------
const Lens: React.FC<{readonly iris: number; readonly glow: number}> = ({iris, glow}) => (
	<g transform="translate(540 760)">
		<circle r={420} fill="url(#whiteGlow)" opacity={0.3 + glow * 0.7} />
		<circle r={330} fill="#11191c" stroke="#9aa5a6" strokeWidth={18} />
		<circle r={290} fill="#1b2d33" stroke="#4d5f64" strokeWidth={8} />
		{/* diafragma (iris) */}
		<g transform={`rotate(${iris * 60})`}>
			{new Array(6).fill(0).map((_, i) => (
				<path
					key={i}
					d={`M0 0 L${280} ${-60} L${280} ${120} Z`}
					fill="#0d1416"
					stroke="#5b6d72"
					strokeWidth={3}
					transform={`rotate(${i * 60}) translate(${40 + iris * 60} 0)`}
				/>
			))}
		</g>
		<circle r={70 + iris * 40} fill="#9fe3ff" opacity={0.6 + glow * 0.4} filter="url(#glow)" />
		<circle r={30} cx={-80} cy={-90} fill="#ffffff" opacity={0.5} />
	</g>
);

export const SkyLens: React.FC<SceneProps> = ({dur}) => {
	const f = useCurrentFrame();
	const part = lerp(f, [0, 0.6 * dur], [0, 1], ease);
	return (
		<Stage bg="#a9c9bf">
			<SkyRect id="sl-sky" stops={[[0, '#4c6a70'], [1, '#d9c59a']]} />
			<g opacity={part}>
				<Lens iris={Math.sin(f * 0.15) * 0.5 + 0.5} glow={0.2} />
			</g>
			{/* nubes que se abren */}
			{[0, 1, 2, 3, 4, 5].map((k) => {
				const side = k % 2 ? 1 : -1;
				return (
					<ellipse
						key={k}
						cx={540 + side * (180 + part * 520) + (k - 3) * 20}
						cy={500 + k * 110}
						rx={360}
						ry={150}
						fill="#e9ecea"
						opacity={0.9}
						filter="url(#soft)"
					/>
				);
			})}
			<path d="M-50 1500 C300 1400 700 1450 1130 1380 L1130 1920 L-50 1920 Z" fill="#3c574e" />
		</Stage>
	);
};

export const LensZoom: React.FC<SceneProps> = ({dur}) => {
	const f = useCurrentFrame();
	return (
		<Camera dur={dur} origin={[540, 760]} scale={[1, 4]} easing={easeIn}>
			<Stage bg="#4c6a70">
				<SkyRect id="lz-sky" stops={[[0, '#4c6a70'], [1, '#d9c59a']]} />
				<Lens iris={0.2} glow={lerp(f, [0, dur], [0.2, 1])} />
				<rect x={0} y={0} width={1080} height={1920} fill="#ffffff" opacity={lerp(f, [0.45 * dur, dur], [0, 1])} />
			</Stage>
		</Camera>
	);
};
