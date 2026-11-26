import React from 'react';
import {AbsoluteFill, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';
import {loadFont} from '@remotion/fonts';
import {C, ease, lerp} from '../lib/base';

// Tipografía Oswald guardada en public/fonts (funciona sin internet).
const fontFamily = 'Oswald';
loadFont({family: fontFamily, url: staticFile('fonts/Oswald-latin.woff2'), weight: '200 700'});
loadFont({family: fontFamily, url: staticFile('fonts/Oswald-latin-ext.woff2'), weight: '200 700', unicodeRange: 'U+0100-024F, U+1E00-1EFF'});

type Timed = {readonly dur: number};

// ---------- Texto "EN VIVO" ----------
export const LiveText: React.FC<Timed> = () => {
	const f = useCurrentFrame();
	const blink = Math.floor(f / 6) % 2 === 0 ? 1 : 0.3;
	return (
		<AbsoluteFill style={{alignItems: 'center', paddingTop: 230}}>
			<div
				style={{
					display: 'flex',
					alignItems: 'center',
					gap: 28,
					padding: '18px 44px',
					borderRadius: 16,
					background: 'rgba(10,14,15,0.75)',
					fontFamily,
					fontWeight: 700,
					fontSize: 104,
					letterSpacing: 8,
					color: C.white,
					scale: String(lerp(f, [0, 6], [1.3, 1], ease)),
				}}
			>
				<div style={{width: 54, height: 54, borderRadius: 27, background: C.red, opacity: blink, boxShadow: `0 0 30px ${C.red}`}} />
				EN VIVO
			</div>
		</AbsoluteFill>
	);
};

// ---------- Texto grande y con golpe ("x2", "48") ----------
export const PunchText: React.FC<Timed & {readonly text: string; readonly color: string; readonly top: number; readonly size: number}> = ({dur, text, color, top, size}) => {
	const f = useCurrentFrame();
	return (
		<AbsoluteFill style={{alignItems: 'center', paddingTop: top}}>
			<div
				style={{
					fontFamily,
					fontWeight: 700,
					fontSize: size,
					lineHeight: 1,
					color,
					textShadow: `0 0 40px ${color}, 0 8px 0 rgba(0,0,0,0.5)`,
					scale: String(lerp(f, [0, 7], [1.8, 1], ease)),
					opacity: lerp(f, [0, 3, dur - 4, dur], [0, 1, 1, 0]),
				}}
			>
				{text}
			</div>
		</AbsoluteFill>
	);
};

// ---------- Tarjeta del título ----------
export const TitleCard: React.FC<Timed> = () => {
	const f = useCurrentFrame();
	const {fps} = useVideoConfig();
	return (
		<AbsoluteFill style={{alignItems: 'center', paddingTop: 150, paddingLeft: 60, paddingRight: 60, background: `linear-gradient(180deg, rgba(5,12,14,${lerp(f, [0, 1 * fps], [0, 0.85])}) 0%, rgba(5,12,14,0) 30%)`}}>
			<div
				style={{
					textAlign: 'center',
					fontFamily,
					opacity: lerp(f, [0, 1 * fps], [0, 1], ease),
					translate: `0 ${lerp(f, [0, 1 * fps], [30, 0], ease)}px`,
				}}
			>
				<div style={{fontWeight: 700, fontSize: 86, lineHeight: 1.05, color: C.white, letterSpacing: 0, whiteSpace: 'nowrap', textShadow: '0 4px 24px rgba(0,0,0,0.8)'}}>
					LOS JUEGOS DEL HAMBRE:
				</div>
				<div style={{fontWeight: 700, fontSize: 86, lineHeight: 1.05, color: C.mustard, letterSpacing: 0, whiteSpace: 'nowrap', textShadow: '0 4px 24px rgba(0,0,0,0.8)'}}>
					AMANECER EN LA COSECHA
				</div>
				<div style={{marginTop: 22, fontWeight: 500, fontSize: 44, color: C.haze, textShadow: '0 2px 12px rgba(0,0,0,0.9)'}}>
					The Hunger Games: Sunrise on the Reaping (2026)
				</div>
			</div>
		</AbsoluteFill>
	);
};

// ---------- Transiciones ----------
export const WhiteFlash: React.FC<Timed> = ({dur}) => {
	const f = useCurrentFrame();
	return <AbsoluteFill style={{background: '#ffffff', opacity: lerp(f, [0, dur * 0.3, dur], [1, 1, 0])}} />;
};

export const BlackHit: React.FC<Timed> = () => <AbsoluteFill style={{background: '#000'}} />;

export const FadeFromWhite: React.FC<Timed> = ({dur}) => {
	const f = useCurrentFrame();
	return <AbsoluteFill style={{background: '#ffffff', opacity: lerp(f, [0, dur], [1, 0])}} />;
};

// ---------- Acabado: pulso en cada medio tiempo, grano y viñeta ----------
// 100 BPM -> medio tiempo = 0,3 s = 9 cuadros a 30 fps.
export const BeatPulse: React.FC<{readonly halfBeat: number}> = ({halfBeat}) => {
	const f = useCurrentFrame();
	const t = (f % halfBeat) / halfBeat;
	return (
		<AbsoluteFill
			style={{
				background: `radial-gradient(circle at 50% 40%, ${C.goldLight} 0%, transparent 70%)`,
				mixBlendMode: 'soft-light',
				opacity: 0.18 * (1 - t) * (1 - t),
			}}
		/>
	);
};

export const Finish: React.FC = () => {
	const f = useCurrentFrame();
	return (
		<AbsoluteFill style={{pointerEvents: 'none'}}>
			{/* bruma verde azulada */}
			<AbsoluteFill style={{background: C.tealMid, mixBlendMode: 'soft-light', opacity: 0.35}} />
			{/* grano de pintura */}
			<svg width="100%" height="100%" style={{position: 'absolute', mixBlendMode: 'overlay', opacity: 0.22}}>
				<filter id="grain">
					<feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="2" seed={Math.floor(f / 2) % 12} />
					<feColorMatrix type="saturate" values="0" />
				</filter>
				<rect width="100%" height="100%" filter="url(#grain)" />
			</svg>
			{/* viñeta */}
			<AbsoluteFill style={{background: 'radial-gradient(ellipse at 50% 50%, transparent 55%, rgba(0,0,0,0.6) 100%)'}} />
		</AbsoluteFill>
	);
};
