#version 120
attribute vec3 coord3d;
uniform mat4 transform;
void main(void) {
  gl_Position = transform * vec4(coord3d, 1.0);
}
