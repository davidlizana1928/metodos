import {Composition} from 'remotion';
import {AmanecerCosecha} from './Video';

export const RemotionRoot: React.FC = () => {
	return (
		<>
			{/* Video vertical 1080x1920 para TikTok, 30 cuadros por segundo, 85 segundos. */}
			<Composition
				id="AmanecerCosecha"
				component={AmanecerCosecha}
				durationInFrames={2550}
				fps={30}
				width={1080}
				height={1920}
			/>
		</>
	);
};
