import { ThreeCanvas } from "@remotion/three";
import { useThree } from "@react-three/fiber";
import { useMemo } from "react";
import { AbsoluteFill, Easing, interpolate, random, useCurrentFrame, useVideoConfig } from "remotion";
import * as THREE from "three";

// Escena de la historia (gancho): una ciudad de noche en alerta, nevando,
// y una camioneta de reparto que va hacia ella por la carretera de montaña.
// Sub-momentos = movimientos de cámara cada 2-3 s, nunca cortes a otro lugar.

const VELOCIDAD = 4.2; // unidades por segundo
const zCamioneta = (t: number) => 6 - VELOCIDAD * t;

const KF = [0, 2.2, 3.84, 5.6, 7.48, 11, 17];
const curva = { easing: Easing.bezier(0.45, 0, 0.25, 1), extrapolateLeft: "clamp" as const, extrapolateRight: "clamp" as const };

const Camara: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = frame / fps;
  const z = zCamioneta(t);
  const camera = useThree((s) => s.camera);
  // a) vista aérea de la ciudad  b) baja hacia la carretera  c) detrás de la camioneta
  // d) se abre al costado con la ciudad cerca  e) sube al cerrar
  camera.position.set(
    interpolate(t, KF, [0, 1, 2, 2.6, -2.8, -4, -3], curva),
    interpolate(t, KF, [42, 26, 4.2, 3.2, 2.4, 6, 16], curva),
    z + interpolate(t, KF, [46, 36, 10, 7.5, 6.5, 10, 22], curva),
  );
  camera.lookAt(0, interpolate(t, KF, [0, 0, 1.6, 1.6, 2, 3, 3], curva), z - interpolate(t, KF, [80, 60, 22, 20, 34, 40, 50], curva));
  camera.updateMatrixWorld();
  return null;
};

const texturaVentanas = (semilla: number) => {
  const c = document.createElement("canvas");
  c.width = 64;
  c.height = 128;
  const g = c.getContext("2d")!;
  g.fillStyle = "#0c1018";
  g.fillRect(0, 0, 64, 128);
  for (let y = 4; y < 124; y += 8) {
    for (let x = 4; x < 60; x += 8) {
      const r = random(`v${semilla}-${x}-${y}`);
      if (r > 0.55) {
        g.fillStyle = r > 0.93 ? "#ff5a4a" : r > 0.75 ? "#ffd59a" : "#8fb4d8";
        g.fillRect(x, y, 4, 5);
      }
    }
  }
  const tx = new THREE.CanvasTexture(c);
  tx.colorSpace = THREE.SRGBColorSpace;
  return tx;
};

const Ciudad: React.FC<{ t: number }> = ({ t }) => {
  const texturas = useMemo(() => [0, 1, 2].map(texturaVentanas), []);
  const edificios = useMemo(() => {
    const out: { x: number; z: number; w: number; h: number; d: number; k: number }[] = [];
    for (let i = 0; i < 110; i++) {
      const x = (random(`x${i}`) - 0.5) * 90;
      if (Math.abs(x) < 5) continue; // deja libre la avenida de entrada
      out.push({
        x,
        z: -70 - random(`z${i}`) * 60,
        w: 4 + random(`w${i}`) * 5,
        h: 6 + random(`h${i}`) ** 2 * 34,
        d: 4 + random(`d${i}`) * 5,
        k: i % 3,
      });
    }
    return out;
  }, []);
  const alarma = 0.6 + 0.4 * Math.sin(t * 5);
  return (
    <>
      {edificios.map((b, i) => (
        <mesh key={i} position={[b.x, b.h / 2, b.z]}>
          <boxGeometry args={[b.w, b.h, b.d]} />
          <meshStandardMaterial color="#0d121b" emissive="#ffffff" emissiveMap={texturas[b.k]} emissiveIntensity={0.9} />
        </mesh>
      ))}
      {/* focos de emergencia y humo sobre la ciudad */}
      {[
        [-18, -85],
        [12, -100],
        [26, -78],
        [-6, -115],
      ].map(([x, z], i) => (
        <group key={i}>
          <pointLight position={[x, 6, z]} intensity={260 * (i % 2 ? alarma : 1.6 - alarma)} distance={40} color={i % 2 ? "#ff2a2a" : "#ff8a2a"} />
          <mesh position={[x, 22, z]}>
            <cylinderGeometry args={[3, 5.5, 34, 16, 1, true]} />
            <meshBasicMaterial color="#2a2830" transparent opacity={0.35} depthWrite={false} />
          </mesh>
        </group>
      ))}
      {/* montañas detrás */}
      {[-60, -30, 0, 30, 60].map((x, i) => (
        <mesh key={x} position={[x, 0, -170]}>
          <coneGeometry args={[38, 40 + (i % 2) * 18, 5]} />
          <meshStandardMaterial color="#0b1220" />
        </mesh>
      ))}
    </>
  );
};

const Camioneta: React.FC<{ z: number; t: number }> = ({ z, t }) => (
  <group position={[0.9, 0, z]} rotation={[0, 0, Math.sin(t * 7) * 0.006]}>
    <mesh position={[0, 1.45, 0.4]}>
      <boxGeometry args={[2.0, 2.1, 3.6]} />
      <meshStandardMaterial color="#e4e8ec" roughness={0.5} />
    </mesh>
    <mesh position={[0, 1.15, -1.9]}>
      <boxGeometry args={[2.0, 1.5, 1.4]} />
      <meshStandardMaterial color="#b9c2ca" roughness={0.5} />
    </mesh>
    <mesh position={[0, 1.55, -2.62]}>
      <boxGeometry args={[1.8, 0.6, 0.05]} />
      <meshStandardMaterial color="#1b2530" metalness={0.6} roughness={0.2} />
    </mesh>
    {[-0.75, 0.75].map((x) => (
      <group key={x}>
        <mesh position={[x, 1.0, 2.22]}>
          <boxGeometry args={[0.25, 0.35, 0.05]} />
          <meshBasicMaterial color="#ff2030" toneMapped={false} />
        </mesh>
        <mesh position={[x, 0.95, -2.62]}>
          <sphereGeometry args={[0.13, 12, 12]} />
          <meshBasicMaterial color="#fff4d0" toneMapped={false} />
        </mesh>
      </group>
    ))}
    {[-1.4, 1.5].map((zz) =>
      [-1.02, 1.02].map((x) => (
        <mesh key={`${zz}${x}`} position={[x, 0.4, zz]} rotation={[0, 0, Math.PI / 2]}>
          <cylinderGeometry args={[0.4, 0.4, 0.3, 20]} />
          <meshStandardMaterial color="#111" />
        </mesh>
      )),
    )}
    <pointLight position={[0, 1.2, -6]} intensity={40} distance={18} color="#fff1cc" />
  </group>
);

const Nieve: React.FC<{ t: number; z: number }> = ({ t, z }) => {
  const pos = useMemo(() => {
    const n = 1600;
    const a = new Float32Array(n * 3);
    for (let i = 0; i < n; i++) {
      a[i * 3] = (random(`nx${i}`) - 0.5) * 50 + Math.sin(t * 0.8 + i) * 0.4;
      a[i * 3 + 1] = (((random(`ny${i}`) * 30 - t * 2.2) % 30) + 30) % 30;
      a[i * 3 + 2] = z + 15 - random(`nz${i}`) * 60;
    }
    return a;
  }, [t, z]);
  return (
    <points>
      <bufferGeometry>
        <bufferAttribute attach="attributes-position" args={[pos, 3]} />
      </bufferGeometry>
      <pointsMaterial size={0.09} color="#eef4ff" transparent opacity={0.85} depthWrite={false} />
    </points>
  );
};

export const HistoriaNocheCero: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps, width, height } = useVideoConfig();
  const t = frame / fps;
  const z = zCamioneta(t);
  return (
    <AbsoluteFill>
    <ThreeCanvas width={width} height={height} camera={{ fov: 55, near: 0.1, far: 400 }}>
      <Camara />
      <color attach="background" args={["#060a13"]} />
      <fog attach="fog" args={["#0b1422", 30, 190]} />
      <ambientLight intensity={0.55} color="#6d86b0" />
      <directionalLight position={[-20, 40, 20]} intensity={0.5} color="#9fb7e0" />
      {/* nieve en el suelo y carretera */}
      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, 0, -60]}>
        <planeGeometry args={[400, 400]} />
        <meshStandardMaterial color="#9eb0c6" roughness={1} />
      </mesh>
      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, 0.02, -40]}>
        <planeGeometry args={[8, 180]} />
        <meshStandardMaterial color="#1d232c" roughness={0.9} />
      </mesh>
      {Array.from({ length: 40 }).map((_, i) => (
        <mesh key={i} rotation={[-Math.PI / 2, 0, 0]} position={[0, 0.03, 40 - i * 4.5]}>
          <planeGeometry args={[0.18, 2]} />
          <meshBasicMaterial color="#e0c060" />
        </mesh>
      ))}
      {Array.from({ length: 36 }).map((_, i) => (
        <mesh key={`p${i}`} position={[i % 2 ? 4.6 : -4.6, 0.6, 40 - Math.floor(i / 2) * 7]}>
          <cylinderGeometry args={[0.06, 0.06, 1.2, 8]} />
          <meshStandardMaterial color="#c9ccd2" />
        </mesh>
      ))}
      <Ciudad t={t} />
      <pointLight position={[1, 5, z + 7]} intensity={45} distance={16} color="#c9d8f0" />
      <Camioneta z={z} t={t} />
      <Nieve t={t} z={z} />
    </ThreeCanvas>
    </AbsoluteFill>
  );
};
