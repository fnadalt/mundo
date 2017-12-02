#version 120

attribute vec4 p3d_Vertex;
attribute vec4 p3d_MultiTexCoord0;
uniform mat4 p3d_ModelMatrix;
uniform mat4 p3d_ModelViewProjectionMatrix;

uniform vec3 light_pos;
uniform vec3 cam_pos;
uniform float altitud_agua;

varying vec4 vpos;
varying vec2 texcoords;
varying vec3 to_cam_vec;
varying vec3 from_light_vec;

void main() {
  vec4 wpos=p3d_ModelMatrix * vec4(p3d_Vertex.x,altitud_agua,p3d_Vertex.y,1.0);
  vpos = p3d_ModelViewProjectionMatrix * p3d_Vertex;
  gl_Position=vpos;
  gl_TexCoord[0] = p3d_MultiTexCoord0;
  texcoords = vec2(p3d_Vertex.x/2.0+0.5, p3d_Vertex.y/2.0+0.5)*1.5;
  to_cam_vec=vec3(cam_pos.x,cam_pos.z,cam_pos.y)-wpos.xyz;
  from_light_vec=wpos.xyz-vec3(light_pos.x,light_pos.z,light_pos.y);
}
