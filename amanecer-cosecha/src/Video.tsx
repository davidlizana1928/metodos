import React from 'react';
import {Audio} from '@remotion/media';
import {AbsoluteFill, Sequence, staticFile, Track, useVideoConfig} from 'remotion';
import {C} from './lib/base';
import {CandleScene, CinemaFinal, CinemaOff, CinemaPush, CinemaTurn, EyeProfile, PlazaScreen, SmokeUrn} from './scenes/Intro';
import {ArenaLights, Fireworks, GoldenVision, MapIcons, MapMarch, MapPulses, MeadowScene, MineExit, MiningTown, VisionShatters} from './scenes/World';
import {
	CameraLenses,
	DomeBlueprint,
	GuardsScene,
	Hatches,
	LensZoom,
	MapIgnite,
	Pendant,
	Platforms,
	Reaping,
	Relief,
	SkyLens,
	SlowMoRun,
	Spotlight,
	StadiumScene,
	TargetLock,
	Train,
	WindowSpectator,
} from './scenes/Capital';
import {BeatPulse, BlackHit, FadeFromWhite, Finish, LiveText, PunchText, TitleCard, WhiteFlash} from './scenes/Overlays';

// Guion visual: "Los Juegos del Hambre: Amanecer en la cosecha".
// Cada <Sequence> es una toma. "from" = segundo en que empieza,
// "durationInFrames" = cuánto dura. Ajusta estos números a tu voz grabada.
export const AmanecerCosecha: React.FC = () => {
	const {fps} = useVideoConfig();
	return (
		<AbsoluteFill style={{background: C.night}}>
			<Track name="Escenas">
				{/* VOZ: "Imagina que el día de tu cumpleaños el gobierno sortea quién va a pelear a muerte… en vivo, por televisión." */}
				<Sequence name="00:00 Cine: empuje al Espectador" from={0} durationInFrames={2 * fps}>
					<CinemaPush dur={2 * fps} />
				</Sequence>
				<Sequence name="00:02 Perfil: luz en el ojo" from={2 * fps} durationInFrames={2 * fps}>
					<EyeProfile dur={2 * fps} />
				</Sequence>
				<Sequence name="00:04 Vela sobre el pan" from={4 * fps} durationInFrames={2 * fps}>
					<CandleScene dur={2 * fps} />
				</Sequence>
				<Sequence name="00:06 El humo dibuja la urna" from={6 * fps} durationInFrames={2 * fps}>
					<SmokeUrn dur={2 * fps} />
				</Sequence>
				<Sequence name="00:08 Pantalla en la plaza" from={8 * fps} durationInFrames={1 * fps}>
					<PlazaScreen dur={1 * fps} />
				</Sequence>

				{/* VOZ: "Cada año, la capital obliga a cada región a entregar jóvenes a unos juegos donde solo uno sobrevive." */}
				<Sequence name="00:09 Mapa: pulsos de la capital" from={9 * fps} durationInFrames={2 * fps}>
					<MapPulses dur={2 * fps} />
				</Sequence>
				<Sequence name="00:11 Mapa: filas hacia la capital" from={11 * fps} durationInFrames={2 * fps}>
					<MapMarch dur={2 * fps} />
				</Sequence>
				<Sequence name="00:13 Arena: queda una luz" from={13 * fps} durationInFrames={3 * fps}>
					<ArenaLights dur={3 * fps} />
				</Sequence>

				{/* VOZ: "Tú vives en una región minera y pobre." */}
				<Sequence name="00:16 Pueblo minero" from={16 * fps} durationInFrames={2 * fps}>
					<MiningTown dur={2 * fps} />
				</Sequence>
				<Sequence name="00:18 El joven sale de la mina" from={18 * fps} durationInFrames={2 * fps}>
					<MineExit dur={2 * fps} />
				</Sequence>

				{/* VOZ: "Tu novia sueña con acabar con esos juegos… pero tú crees que nadie puede vencer a la capital." */}
				<Sequence name="00:20 Pradera con el árbol" from={20 * fps} durationInFrames={2 * fps}>
					<MeadowScene dur={2 * fps} />
				</Sequence>
				<Sequence name="00:22 Visión dorada: pueblo libre" from={22 * fps} durationInFrames={3 * fps}>
					<GoldenVision dur={3 * fps} />
				</Sequence>
				<Sequence name="00:25 La visión se rompe" from={25 * fps} durationInFrames={3 * fps}>
					<VisionShatters dur={3 * fps} />
				</Sequence>

				{/* VOZ: "Pero este año los juegos cumplen cincuenta, y se llevan el doble: cuatro jóvenes por región." */}
				<Sequence name="00:28 Fuegos artificiales" from={28 * fps} durationInFrames={2 * fps}>
					<Fireworks dur={2 * fps} />
				</Sequence>
				<Sequence name="00:30 Mapa: dos íconos" from={30 * fps} durationInFrames={2 * fps}>
					<MapIcons dur={2 * fps} />
				</Sequence>
				<Sequence name="00:32 Mapa: se dividen en cuatro" from={32 * fps} durationInFrames={2 * fps}>
					<MapIcons dur={2 * fps} split />
				</Sequence>

				{/* VOZ: "Y lo peor es que tu nombre no sale sorteado… pero cuando los guardias van contra tu novia, la defiendes." */}
				<Sequence name="00:34 Sorteo y multitud" from={34 * fps} durationInFrames={3 * fps}>
					<Reaping dur={3 * fps} />
				</Sequence>
				<Sequence name="00:37 Alivio" from={37 * fps} durationInFrames={2 * fps}>
					<Relief dur={2 * fps} />
				</Sequence>
				<Sequence name="00:39 Ella avanza hacia los guardias" from={39 * fps} durationInFrames={2 * fps}>
					<GuardsScene dur={2 * fps} />
				</Sequence>
				<Sequence name="00:41 Cámara lenta: la defiende" from={41 * fps} durationInFrames={2 * fps}>
					<SlowMoRun dur={2 * fps} />
				</Sequence>

				{/* VOZ: "Y como castigo, te eligen a ti." */}
				<Sequence name="00:43 Foco blanco" from={43 * fps} durationInFrames={3 * fps}>
					<Spotlight dur={3 * fps} />
				</Sequence>

				{/* VOZ: "En la capital, frente a las cámaras, te burlas del presidente…" */}
				<Sequence name="00:46 Tren hacia la capital" from={46 * fps} durationInFrames={2 * fps}>
					<Train dur={2 * fps} />
				</Sequence>
				<Sequence name="00:48 Estadio: aplauso con burla" from={48 * fps} durationInFrames={3 * fps}>
					<StadiumScene dur={3 * fps} />
				</Sequence>

				{/* VOZ: "Lo que no sabes es que desde ese momento te tiene en la mira." */}
				<Sequence name="00:51 Marcador rojo" from={51 * fps} durationInFrames={3 * fps}>
					<TargetLock dur={3 * fps} />
				</Sequence>
				<Sequence name="00:54 Lentes rojos en la capital" from={54 * fps} durationInFrames={3 * fps}>
					<CameraLenses dur={3 * fps} />
				</Sequence>

				{/* VOZ: "Entonces decides que no vas a pelear solo para sobrevivir: vas a pelear para que todo el país vea que se puede desafiar al gobierno." */}
				<Sequence name="00:57 Manos con el colgante" from={57 * fps} durationInFrames={2 * fps}>
					<Pendant dur={2 * fps} />
				</Sequence>
				<Sequence name="00:59 Plano de la cúpula" from={59 * fps} durationInFrames={3 * fps}>
					<DomeBlueprint dur={3 * fps} />
				</Sequence>
				<Sequence name="01:02 Mapa: regiones encendidas" from={62 * fps} durationInFrames={3 * fps}>
					<MapIgnite dur={3 * fps} />
				</Sequence>
				<Sequence name="01:05 Espectador en la ventana" from={65 * fps} durationInFrames={2 * fps}>
					<WindowSpectator dur={2 * fps} />
				</Sequence>

				{/* VOZ: "Y justo cuando entras a la arena con otros cuarenta y siete… entiendes que tu verdadero enemigo no está ahí adentro." */}
				<Sequence name="01:07 Escotillas en el valle" from={67 * fps} durationInFrames={3 * fps}>
					<Hatches dur={3 * fps} />
				</Sequence>
				<Sequence name="01:10 Plataformas encendidas" from={70 * fps} durationInFrames={2 * fps}>
					<Platforms dur={2 * fps} />
				</Sequence>
				<Sequence name="01:12 Lente en el cielo" from={72 * fps} durationInFrames={2 * fps}>
					<SkyLens dur={2 * fps} />
				</Sequence>
				<Sequence name="01:14 Acercamiento al lente" from={74 * fps} durationInFrames={2 * fps}>
					<LensZoom dur={2 * fps} />
				</Sequence>

				{/* VOZ: "Se trata de Los Juegos del Hambre: Amanecer en la cosecha… Si fueras tú, ¿obedecerías o te rebelarías?" */}
				<Sequence name="01:16 Cine: acercamiento lento" from={76 * fps} durationInFrames={3 * fps}>
					<CinemaFinal dur={3 * fps} />
				</Sequence>
				<Sequence name="01:19 El Espectador gira la cabeza" from={79 * fps} durationInFrames={3 * fps}>
					<CinemaTurn dur={3 * fps} />
				</Sequence>
				<Sequence name="01:22 La pantalla se apaga" from={82 * fps} durationInFrames={3 * fps}>
					<CinemaOff dur={3 * fps} />
				</Sequence>
			</Track>

			<Finish />
			<BeatPulse halfBeat={Math.round(0.3 * fps)} />

			<Track name="Transiciones">
				<Sequence name="Destello blanco" from={3.8 * fps} durationInFrames={0.5 * fps}>
					<WhiteFlash dur={0.5 * fps} />
				</Sequence>
				<Sequence name="Golpe negro 0,3 s" from={45.7 * fps} durationInFrames={0.3 * fps}>
					<BlackHit dur={0.3 * fps} />
				</Sequence>
				<Sequence name="Salida del blanco" from={76 * fps} durationInFrames={0.6 * fps}>
					<FadeFromWhite dur={0.6 * fps} />
				</Sequence>
			</Track>

			<Track name="Texto en pantalla">
				<Sequence name="EN VIVO" from={8 * fps} durationInFrames={1 * fps}>
					<LiveText dur={1 * fps} />
				</Sequence>
				<Sequence name="x2" from={32.3 * fps} durationInFrames={1.7 * fps}>
					<PunchText dur={1.7 * fps} text="x2" color={C.red} top={180} size={320} />
				</Sequence>
				<Sequence name="48" from={67.5 * fps} durationInFrames={2.5 * fps}>
					<PunchText dur={2.5 * fps} text="48" color={C.white} top={200} size={360} />
				</Sequence>
				<Sequence name="Título" from={76 * fps} durationInFrames={9 * fps}>
					<TitleCard dur={9 * fps} />
				</Sequence>
			</Track>

			{/* Voz generada con Kokoro (voz "em_alex", español). Mueve "from" para ajustar cada frase. */}
			<Track name="Voz">
				<Audio
					name="Voz 1: Imagina que el día de tu cumpleaños, el…"
					src={staticFile('voz/voz-00.wav')}
					from={0.2 * fps}
					durationInFrames={188}
				/>
				<Audio
					name="Voz 2: Cada año, la capital obliga a cada regió…"
					src={staticFile('voz/voz-01.wav')}
					from={9.2 * fps}
					durationInFrames={190}
				/>
				<Audio
					name="Voz 3: Tú vives en una región minera y pobre…"
					src={staticFile('voz/voz-02.wav')}
					from={16.2 * fps}
					durationInFrames={73}
				/>
				<Audio
					name="Voz 4: Tu novia sueña con acabar con esos juego…"
					src={staticFile('voz/voz-03.wav')}
					from={20.2 * fps}
					durationInFrames={161}
				/>
				<Audio
					name="Voz 5: Pero este año los juegos cumplen cincuen…"
					src={staticFile('voz/voz-04.wav')}
					from={28.2 * fps}
					durationInFrames={156}
				/>
				<Audio
					name="Voz 6: Y lo peor es que tu nombre no sale sorte…"
					src={staticFile('voz/voz-05.wav')}
					from={34.2 * fps}
					durationInFrames={181}
				/>
				<Audio
					name="Voz 7: Y como castigo, te eligen a ti…"
					src={staticFile('voz/voz-06.wav')}
					from={43.2 * fps}
					durationInFrames={62}
				/>
				<Audio
					name="Voz 8: En la capital, frente a las cámaras, te…"
					src={staticFile('voz/voz-07.wav')}
					from={46.2 * fps}
					durationInFrames={104}
				/>
				<Audio
					name="Voz 9: Lo que no sabes es que desde ese momento…"
					src={staticFile('voz/voz-08.wav')}
					from={51.2 * fps}
					durationInFrames={106}
				/>
				<Audio
					name="Voz 10: Entonces decides que no vas a pelear sol…"
					src={staticFile('voz/voz-09.wav')}
					from={57.2 * fps}
					durationInFrames={233}
				/>
				<Audio
					name="Voz 11: Y justo cuando entras a la arena con otr…"
					src={staticFile('voz/voz-10.wav')}
					from={67.2 * fps}
					durationInFrames={199}
				/>
				<Audio
					name="Voz 12: Se trata de Los Juegos del Hambre: Amane…"
					src={staticFile('voz/voz-11.wav')}
					from={76.2 * fps}
					durationInFrames={176}
				/>
			</Track>
		</AbsoluteFill>
	);
};
