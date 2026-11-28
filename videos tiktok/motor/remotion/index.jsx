import {registerRoot, Composition, AbsoluteFill, useCurrentFrame, interpolate} from 'remotion';
const Prueba = () => {
  const f = useCurrentFrame();
  return <AbsoluteFill style={{background:'#0b1a1c',justifyContent:'center',alignItems:'center'}}>
    <div style={{color:'#f4ead2',fontSize:110,fontFamily:'sans-serif',fontWeight:900,opacity:interpolate(f,[0,15],[0,1],{extrapolateRight:'clamp'})}}>Remotion OK</div>
  </AbsoluteFill>;
};
const Root = () => <Composition id="prueba" component={Prueba} durationInFrames={30} fps={30} width={1080} height={1920}/>;
registerRoot(Root);
