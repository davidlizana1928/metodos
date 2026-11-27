import { ThreeCanvas } from "@remotion/three";
import { useThree } from "@react-three/fiber";
import { useMemo } from "react";
import { random, useCurrentFrame, useVideoConfig } from "remotion";
import * as THREE from "three";
import { cameraAt, FOV, SCREEN, screenPower } from "./camera";

const SEAT_RED = "#8f1d2a";
const ROWS_Z = [5.6, 4.35, 3.1, 1.85, 0.6, -0.65, -1.9, -3.15];
const SEATS_X = [-5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5];
const rowBase = (z: number) => (z + 4) * 0.16; // gradas: las filas de atrás están más altas
const SPECTATOR_Z = 4.35;
const PROJECTOR = new THREE.Vector3(0, 7.2, 11.5);

const CameraRig: React.FC = () => {
  const frame = useCurrentFrame();
  const camera = useThree((s) => s.camera);
  const { position, target, roll } = cameraAt(frame);
  camera.position.copy(position);
  camera.lookAt(target);
  camera.rotateZ(roll);
  camera.updateMatrixWorld();
  return null;
};

const Seat: React.FC<{ x: number; z: number }> = ({ x, z }) => {
  const y = rowBase(z);
  return (
    <group position={[x, y, z]}>
      <mesh position={[0, 0.45, 0]}>
        <boxGeometry args={[0.86, 0.2, 0.7]} />
        <meshStandardMaterial color={SEAT_RED} roughness={0.85} />
      </mesh>
      <mesh position={[0, 0.98, 0.32]} rotation={[-0.12, 0, 0]}>
        <boxGeometry args={[0.86, 0.95, 0.16]} />
        <meshStandardMaterial color={SEAT_RED} roughness={0.85} />
      </mesh>
      <mesh position={[0, 1.47, 0.38]} rotation={[-0.12, 0, 0]}>
        <boxGeometry args={[0.8, 0.08, 0.17]} />
        <meshStandardMaterial color="#b33241" roughness={0.6} />
      </mesh>
    </group>
  );
};

// El espectador del avatar: pelo oscuro y buzo amarillo, de espaldas
const Spectator: React.FC = () => {
  const y = rowBase(SPECTATOR_Z);
  return (
    <group position={[0, y, SPECTATOR_Z - 0.05]}>
      <mesh position={[0, 1.05, 0.05]}>
        <capsuleGeometry args={[0.36, 0.35, 8, 24]} />
        <meshStandardMaterial color="#e0aa22" roughness={0.7} />
      </mesh>
      <mesh position={[0, 1.42, 0.12]} rotation={[0.25, 0, 0]}>
        <torusGeometry args={[0.24, 0.09, 12, 32]} />
        <meshStandardMaterial color="#c8921a" roughness={0.7} />
      </mesh>
      <mesh position={[0, 1.78, 0.03]}>
        <sphereGeometry args={[0.27, 32, 32]} />
        <meshStandardMaterial color="#2b1a12" roughness={0.9} />
      </mesh>
      <mesh position={[0, 1.86, 0.06]} scale={[1.04, 0.9, 1.04]}>
        <sphereGeometry args={[0.27, 32, 32, 0, Math.PI * 2, 0, Math.PI / 1.7]} />
        <meshStandardMaterial color="#160d09" roughness={1} />
      </mesh>
    </group>
  );
};

const ProjectorBeam: React.FC<{ power: number }> = ({ power }) => {
  const frame = useCurrentFrame();
  const { mid, quat, length } = useMemo(() => {
    const end = new THREE.Vector3(SCREEN.x, SCREEN.y, SCREEN.z + 1.5);
    const dir = end.clone().sub(PROJECTOR);
    const q = new THREE.Quaternion().setFromUnitVectors(
      new THREE.Vector3(0, -1, 0),
      dir.clone().normalize(),
    );
    return {
      mid: PROJECTOR.clone().add(end).multiplyScalar(0.5),
      quat: q,
      length: dir.length(),
    };
  }, []);

  // Polvo flotando en el haz de luz (posiciones fijas por semilla, movimiento según el frame)
  const dust = useMemo(() => {
    const arr = new Float32Array(420 * 3);
    const end = new THREE.Vector3(SCREEN.x, SCREEN.y, SCREEN.z);
    for (let i = 0; i < 420; i++) {
      const t = 0.2 + 0.75 * random(`t${i}`);
      const p = PROJECTOR.clone().lerp(end, t);
      const r = t * 2.6 * Math.sqrt(random(`r${i}`));
      const a = random(`a${i}`) * Math.PI * 2;
      arr[i * 3] = p.x + Math.cos(a) * r;
      arr[i * 3 + 1] = p.y + Math.sin(a) * r * 0.6;
      arr[i * 3 + 2] = p.z;
    }
    return arr;
  }, []);
  const moved = useMemo(() => {
    const out = new Float32Array(dust.length);
    for (let i = 0; i < dust.length; i += 3) {
      const k = i / 3;
      out[i] = dust[i] + Math.sin(frame / 30 + k) * 0.08;
      out[i + 1] = dust[i + 1] + Math.sin(frame / 45 + k * 1.7) * 0.1;
      out[i + 2] = dust[i + 2] + Math.cos(frame / 40 + k) * 0.06;
    }
    return out;
  }, [dust, frame]);

  return (
    <>
      <mesh position={mid} quaternion={quat}>
        <coneGeometry args={[3.1, length, 48, 1, true]} />
        <meshBasicMaterial
          color="#b9d3ff"
          transparent
          opacity={0.045 * power}
          blending={THREE.AdditiveBlending}
          depthWrite={false}
          side={THREE.DoubleSide}
        />
      </mesh>
      <points>
        <bufferGeometry>
          <bufferAttribute attach="attributes-position" args={[moved, 3]} />
        </bufferGeometry>
        <pointsMaterial
          size={0.022}
          color="#e8f1ff"
          transparent
          opacity={0.85 * power}
          blending={THREE.AdditiveBlending}
          depthWrite={false}
        />
      </points>
    </>
  );
};

const Room: React.FC<{ power: number }> = ({ power }) => {
  const screenColor = new THREE.Color("#0b0d14").lerp(
    new THREE.Color("#eef3fb"),
    power,
  );
  return (
    <>
      {/* Pantalla */}
      <mesh position={[SCREEN.x, SCREEN.y, SCREEN.z - 0.12]}>
        <boxGeometry args={[SCREEN.w + 0.5, SCREEN.h + 0.5, 0.1]} />
        <meshStandardMaterial color="#05060a" />
      </mesh>
      <mesh position={[SCREEN.x, SCREEN.y, SCREEN.z]}>
        <planeGeometry args={[SCREEN.w, SCREEN.h]} />
        <meshBasicMaterial color={screenColor} toneMapped={false} />
      </mesh>
      {/* Telones rojos */}
      {[-1, 1].map((side) =>
        [0, 1, 2, 3].map((i) => (
          <mesh
            key={`${side}-${i}`}
            position={[side * (SCREEN.w / 2 + 0.55 + i * 0.42), 4.4, SCREEN.z + 0.3]}
          >
            <cylinderGeometry args={[0.24, 0.3, 9, 16]} />
            <meshStandardMaterial color="#6e0f1d" roughness={0.9} />
          </mesh>
        )),
      )}
      {/* Paredes, techo y piso */}
      <mesh position={[0, 0, 0]} rotation={[-Math.PI / 2, 0, 0]}>
        <planeGeometry args={[30, 40]} />
        <meshStandardMaterial color="#141522" />
      </mesh>
      <mesh position={[0, 9, 0]} rotation={[Math.PI / 2, 0, 0]}>
        <planeGeometry args={[30, 40]} />
        <meshStandardMaterial color="#3d0f1b" />
      </mesh>
      {[-1, 1].map((side) => (
        <mesh key={side} position={[side * 7.6, 4.5, 0]} rotation={[0, -side * Math.PI / 2, 0]}>
          <planeGeometry args={[40, 9]} />
          <meshStandardMaterial color="#1a1e33" />
        </mesh>
      ))}
      <mesh position={[0, 4.5, SCREEN.z - 0.3]}>
        <planeGeometry args={[30, 9]} />
        <meshStandardMaterial color="#120d18" />
      </mesh>
      {/* Gradas bajo cada fila */}
      {ROWS_Z.map((z) => (
        <mesh key={z} position={[0, rowBase(z) / 2, z + 0.1]}>
          <boxGeometry args={[12.5, Math.max(rowBase(z), 0.02), 1.25]} />
          <meshStandardMaterial color="#1b1b2b" />
        </mesh>
      ))}
      {/* Luces guía del pasillo */}
      {ROWS_Z.map((z) => (
        <mesh key={`l${z}`} position={[-6.1, rowBase(z) + 0.05, z]}>
          <sphereGeometry args={[0.05, 12, 12]} />
          <meshBasicMaterial color="#ffb347" toneMapped={false} />
        </mesh>
      ))}
    </>
  );
};

export const CinemaScene: React.FC = () => {
  const frame = useCurrentFrame();
  const { width, height } = useVideoConfig();
  const power = screenPower(frame);

  return (
    <ThreeCanvas
      width={width}
      height={height}
      camera={{ fov: FOV, near: 0.1, far: 200, position: [0, 2.2, 7.4] }}
    >
      <CameraRig />
      <color attach="background" args={["#05050a"]} />
      <fog attach="fog" args={["#07070d", 12, 34]} />
      <ambientLight intensity={0.9 + 0.2 * power} color="#5a6aa8" />
      <pointLight
        position={[0, SCREEN.y, SCREEN.z + 3]}
        intensity={140 * power}
        distance={30}
        decay={1.6}
        color="#cfe0ff"
      />
      <pointLight position={[-5, 6, 8]} intensity={30} distance={16} color="#ff4d5e" />
      <pointLight position={[5, 6, 8]} intensity={22} distance={16} color="#38d9e8" />
      <pointLight position={[0, 6.8, 9.5]} intensity={20 * power} distance={12} color="#b9d3ff" />
      <pointLight position={[0, 3.2, 2.2]} intensity={6 + 10 * power} distance={5} color="#ffd9a0" />
      <Room power={power} />
      {ROWS_Z.map((z) =>
        SEATS_X.filter((x) => !(z === SPECTATOR_Z && x === 0)).map((x) => (
          <Seat key={`${x}:${z}`} x={x} z={z} />
        )),
      )}
      <Seat x={0} z={SPECTATOR_Z} />
      <Spectator />
      <ProjectorBeam power={power} />
    </ThreeCanvas>
  );
};
