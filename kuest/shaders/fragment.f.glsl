#version 120
varying float height;

void main(void) {
  gl_FragColor[0] = 0.5;
  gl_FragColor[1] = clamp(height, 0.0, 1.0);
  gl_FragColor[2] = 0.5;
}
