#version 120
attribute vec3 coord3d;
uniform mat4 mvp;
varying float height;
void main(void) {
  height = coord3d.y;
  gl_Position = mvp * vec4(coord3d, 1.0);
}
