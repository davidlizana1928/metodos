import { Easing, interpolate } from "remotion";
import * as THREE from "three";

// Medidas de la sala (en "metros" de la escena 3D)
export const SCREEN = { x: 0, y: 3.8, z: -12, w: 9.6, h: 5.4 };
export const FOV = 62;

// Recorrido de cámara: arranca detrás del espectador y vuela hacia la pantalla
export const cameraAt = (frame: number) => {
  const p = interpolate(frame, [0, 170], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.bezier(0.55, 0, 0.25, 1),
  });
  const sway = Math.sin(frame / 22) * 0.04 * (1 - p);
  return {
    position: new THREE.Vector3(
      interpolate(p, [0, 1], [0.75, 0]) + sway,
      interpolate(p, [0, 0.5, 1], [3.6, 3.85, 3.6]),
      interpolate(p, [0, 1], [6.4, 2.2]),
    ),
    target: new THREE.Vector3(0, interpolate(p, [0, 1], [3.15, 3.7]), SCREEN.z),
    roll: interpolate(p, [0, 1], [-0.03, 0]),
  };
};

// Calcula dónde cae la pantalla del cine en el video (en píxeles),
// para poder dibujar el texto 2D exactamente encima.
export const projectScreen = (frame: number, width: number, height: number) => {
  const { position, target, roll } = cameraAt(frame);
  const cam = new THREE.PerspectiveCamera(FOV, width / height, 0.1, 200);
  cam.position.copy(position);
  cam.lookAt(target);
  cam.rotateZ(roll);
  cam.updateMatrixWorld();
  const corners = [
    [-1, 1],
    [1, 1],
    [1, -1],
    [-1, -1],
  ].map(([sx, sy]) => {
    const v = new THREE.Vector3(
      SCREEN.x + (sx * SCREEN.w) / 2,
      SCREEN.y + (sy * SCREEN.h) / 2,
      SCREEN.z,
    ).project(cam);
    return { x: ((v.x + 1) / 2) * width, y: ((1 - v.y) / 2) * height };
  });
  const xs = corners.map((c) => c.x);
  const ys = corners.map((c) => c.y);
  const left = Math.min(...xs);
  const top = Math.min(...ys);
  return {
    left,
    top,
    width: Math.max(...xs) - left,
    height: Math.max(...ys) - top,
  };
};

// Cuánto está encendida la pantalla (0 = apagada, 1 = encendida), con parpadeo de proyector
export const screenPower = (frame: number) => {
  const on = interpolate(frame, [38, 62], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const flicker =
    frame > 38 && frame < 64 ? (Math.sin(frame * 2.7) > 0.2 ? 1 : 0.35) : 1;
  return on * flicker;
};
