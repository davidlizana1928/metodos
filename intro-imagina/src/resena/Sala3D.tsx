import { ThreeCanvas } from "@remotion/three";
import { useThree } from "@react-three/fiber";
import { useMemo } from "react";
import { AbsoluteFill, random, useCurrentFrame, useVideoConfig } from "remotion";
import * as THREE from "three";
import { FOV, PANTALLA, poseSala, PROYECTOR } from "./camara";

// Paleta del canal: carmesí, mostaza y bruma verde azulada
const CARMESI = "#8c1a2b";
const MOSTAZA = "#d98b1e";
const BRUMA = "#0d2629";

const FILAS_Z = [5.6, 4.35, 3.1, 1.85, 0.6, -0.65, -1.9, -3.15];
const BUTACAS_X = [-4, -3, -2, -1, 0, 1, 2, 3, 4];
const base = (z: number) => (z + 4) * 0.16;
const Z_ESPECTADOR = 4.35;

const Camara: React.FC<{ p: number }> = ({ p }) => {
  const camera = useThree((s) => s.camera);
  const { position, target } = poseSala(p);
  camera.position.copy(position);
  camera.lookAt(target);
  camera.updateMatrixWorld();
  return null;
};

const Butaca: React.FC<{ x: number; z: number }> = ({ x, z }) => (
  <group position={[x, base(z), z]}>
    <mesh position={[0, 0.45, 0]}>
      <boxGeometry args={[0.86, 0.2, 0.7]} />
      <meshStandardMaterial color={CARMESI} roughness={0.85} />
    </mesh>
    <mesh position={[0, 0.98, 0.32]} rotation={[-0.12, 0, 0]}>
      <boxGeometry args={[0.86, 0.95, 0.16]} />
      <meshStandardMaterial color={CARMESI} roughness={0.85} />
    </mesh>
    <mesh position={[0, 1.47, 0.38]} rotation={[-0.12, 0, 0]}>
      <boxGeometry args={[0.8, 0.08, 0.17]} />
      <meshStandardMaterial color="#b3303f" roughness={0.6} />
    </mesh>
  </group>
);

// El Espectador: pelo oscuro corto con costados rebajados y capucha mostaza.
// Hombros ≈ 0,8 × ancho de butaca. Siempre de espaldas.
const Espectador: React.FC = () => (
  <group position={[0, base(Z_ESPECTADOR), Z_ESPECTADOR - 0.05]}>
    <mesh position={[0, 1.05, 0.05]} scale={[1, 1, 0.75]}>
      <capsuleGeometry args={[0.34, 0.32, 8, 24]} />
      <meshStandardMaterial color={MOSTAZA} roughness={0.75} />
    </mesh>
    {/* capucha caída sobre la espalda */}
    <mesh position={[0, 1.4, 0.2]} rotation={[0.5, 0, 0]} scale={[1, 0.8, 1]}>
      <torusGeometry args={[0.2, 0.1, 12, 32]} />
      <meshStandardMaterial color="#c07612" roughness={0.8} />
    </mesh>
    {/* cabeza: piel en los costados rebajados, pelo oscuro arriba */}
    <mesh position={[0, 1.76, 0.03]}>
      <sphereGeometry args={[0.24, 32, 32]} />
      <meshStandardMaterial color="#6b4630" roughness={0.9} />
    </mesh>
    <mesh position={[0, 1.79, 0.03]} scale={[1.03, 1, 1.03]}>
      <sphereGeometry args={[0.245, 32, 32, 0, Math.PI * 2, 0, Math.PI / 2.4]} />
      <meshStandardMaterial color="#15100c" roughness={1} />
    </mesh>
  </group>
);

const Haz: React.FC<{ potencia: number }> = ({ potencia }) => {
  const frame = useCurrentFrame();
  const fin = useMemo(() => new THREE.Vector3(PANTALLA.x, PANTALLA.y, PANTALLA.z + 1.2), []);
  const { mid, quat, largo } = useMemo(() => {
    const dir = fin.clone().sub(PROYECTOR);
    return {
      mid: PROYECTOR.clone().add(fin).multiplyScalar(0.5),
      quat: new THREE.Quaternion().setFromUnitVectors(new THREE.Vector3(0, -1, 0), dir.clone().normalize()),
      largo: dir.length(),
    };
  }, [fin]);
  const polvo = useMemo(() => {
    const out = new Float32Array(380 * 3);
    for (let i = 0; i < 380; i++) {
      const t = 0.05 + 0.9 * random(`t${i}`);
      const q = PROYECTOR.clone().lerp(fin, t);
      const r = t * 2.8 * Math.sqrt(random(`r${i}`));
      const a = random(`a${i}`) * Math.PI * 2;
      out[i * 3] = q.x + Math.cos(a) * r + Math.sin(frame / 30 + i) * 0.08;
      out[i * 3 + 1] = q.y + Math.sin(a) * r * 0.6 + Math.sin(frame / 45 + i * 1.7) * 0.1;
      out[i * 3 + 2] = q.z + Math.cos(frame / 40 + i) * 0.06;
    }
    return out;
  }, [fin, frame]);
  return (
    <>
      <mesh position={mid} quaternion={quat}>
        <coneGeometry args={[3.0, largo, 48, 1, true]} />
        <meshBasicMaterial color="#cfe6e0" transparent opacity={0.07 * potencia} blending={THREE.AdditiveBlending} depthWrite={false} side={THREE.DoubleSide} />
      </mesh>
      <mesh position={[PROYECTOR.x - 0.1, PROYECTOR.y + 0.05, PROYECTOR.z + 0.45]}>
        <boxGeometry args={[0.7, 0.5, 0.9]} />
        <meshStandardMaterial color="#1b2224" metalness={0.4} roughness={0.5} />
      </mesh>
      <mesh position={[PROYECTOR.x - 0.1, PROYECTOR.y + 0.9, PROYECTOR.z + 0.45]}>
        <cylinderGeometry args={[0.03, 0.03, 1.4, 8]} />
        <meshStandardMaterial color="#1b2224" />
      </mesh>
      <mesh position={PROYECTOR}>
        <sphereGeometry args={[0.16, 16, 16]} />
        <meshBasicMaterial color="#fff6dc" toneMapped={false} />
      </mesh>
      <points>
        <bufferGeometry>
          <bufferAttribute attach="attributes-position" args={[polvo, 3]} />
        </bufferGeometry>
        <pointsMaterial size={0.022} color="#eef6f2" transparent opacity={0.8 * potencia} blending={THREE.AdditiveBlending} depthWrite={false} />
      </points>
    </>
  );
};

const Luces: React.FC = () => (
  <>
    <ambientLight intensity={0.9} color="#4f8a86" />
    <pointLight position={[0, PANTALLA.y, PANTALLA.z + 3]} intensity={120} distance={30} decay={1.6} color="#d8ece8" />
    <pointLight position={[-5, 6, 8]} intensity={26} distance={16} color="#ff4d5e" />
    <pointLight position={[5, 6, 8]} intensity={20} distance={16} color={MOSTAZA} />
    <pointLight position={[0, 3.2, 2.2]} intensity={14} distance={5} color="#ffd9a0" />
  </>
);

// Capa de FONDO: paredes, techo, telones y marco de la pantalla.
// La pantalla queda "vacía": la historia se dibuja encima en 2D/3D.
export const SalaFondo: React.FC<{ p: number }> = ({ p }) => {
  const { width, height } = useVideoConfig();
  return (
    <AbsoluteFill>
    <ThreeCanvas width={width} height={height} camera={{ fov: FOV, near: 0.1, far: 200 }}>
      <Camara p={p} />
      <color attach="background" args={["#050a0b"]} />
      <fog attach="fog" args={[BRUMA, 10, 32]} />
      <Luces />
      <mesh position={[PANTALLA.x, PANTALLA.y, PANTALLA.z - 0.1]}>
        <boxGeometry args={[PANTALLA.w + 0.5, PANTALLA.h + 0.5, 0.1]} />
        <meshStandardMaterial color="#05060a" />
      </mesh>
      {[-1, 1].map((s) =>
        [0, 1, 2, 3].map((i) => (
          <mesh key={`${s}${i}`} position={[s * (PANTALLA.w / 2 + 0.55 + i * 0.42), 4.4, PANTALLA.z + 0.3]}>
            <cylinderGeometry args={[0.24, 0.3, 9, 16]} />
            <meshStandardMaterial color="#6e0f1d" roughness={0.9} />
          </mesh>
        )),
      )}
      <mesh rotation={[-Math.PI / 2, 0, 0]}>
        <planeGeometry args={[30, 40]} />
        <meshStandardMaterial color="#0f1a1c" />
      </mesh>
      <mesh position={[0, 9, 0]} rotation={[Math.PI / 2, 0, 0]}>
        <planeGeometry args={[30, 40]} />
        <meshStandardMaterial color="#10292b" />
      </mesh>
      {[-1, 1].map((s) => (
        <mesh key={s} position={[s * 6.6, 4.5, 0]} rotation={[0, (-s * Math.PI) / 2, 0]}>
          <planeGeometry args={[40, 9]} />
          <meshStandardMaterial color="#14302f" />
        </mesh>
      ))}
      <mesh position={[0, 4.5, PANTALLA.z - 0.3]}>
        <planeGeometry args={[30, 9]} />
        <meshStandardMaterial color="#0a1414" />
      </mesh>
    </ThreeCanvas>
    </AbsoluteFill>
  );
};

// Capa de FRENTE: butacas, Espectador y haz del proyector (van delante de la pantalla).
export const SalaFrente: React.FC<{ p: number }> = ({ p }) => {
  const { width, height } = useVideoConfig();
  return (
    <AbsoluteFill>
    <ThreeCanvas width={width} height={height} camera={{ fov: FOV, near: 0.1, far: 200 }}>
      <Camara p={p} />
      <fog attach="fog" args={[BRUMA, 10, 32]} />
      <Luces />
      {FILAS_Z.map((z) => (
        <mesh key={z} position={[0, base(z) / 2, z + 0.1]}>
          <boxGeometry args={[10, Math.max(base(z), 0.02), 1.25]} />
          <meshStandardMaterial color="#121c1e" />
        </mesh>
      ))}
      {FILAS_Z.map((z) => (
        <mesh key={`l${z}`} position={[-5.2, base(z) + 0.05, z]}>
          <sphereGeometry args={[0.05, 12, 12]} />
          <meshBasicMaterial color={MOSTAZA} toneMapped={false} />
        </mesh>
      ))}
      {FILAS_Z.map((z) => BUTACAS_X.map((x) => <Butaca key={`${x}:${z}`} x={x} z={z} />))}
      <Espectador />
      <Haz potencia={1 - p} />
    </ThreeCanvas>
    </AbsoluteFill>
  );
};
