from panda3d.core import *
load_prc_file_data("", "framebuffer-srgb #t")
#load_prc_file_data("", "gl-support-shadow-filter false")
load_prc_file_data("", "default-fov 90")
import math

from direct.showbase.ShowBase import ShowBase
from direct.interval.IntervalGlobal import Parallel, Sequence
base = ShowBase()

EXPONENT = 128
BRIGHTNESS = 1
DIST = 0.5

shader = Shader.make(Shader.SL_GLSL, """
#version 330

uniform mat4 p3d_ModelViewProjectionMatrix;
uniform mat4 p3d_ModelViewMatrix;
uniform mat3 p3d_NormalMatrix;

in vec4 vertex;
in vec3 normal;

out vec3 vpos;
out vec3 norm;
out vec4 shad[3];

uniform struct {
  vec4 position;
  vec4 diffuse;
  vec4 specular;
  vec3 attenuation;
  vec3 spotDirection;
  float spotCosCutoff;
  float spotExponent;
  sampler2DShadow shadowMap;
  mat4 shadowMatrix;
} p3d_LightSource[3];

void main() {
  gl_Position = p3d_ModelViewProjectionMatrix * vertex;
  vpos = vec3(p3d_ModelViewMatrix * vertex);
  norm = normalize(p3d_NormalMatrix * normal);
  shad[0] = p3d_LightSource[0].shadowMatrix * vertex;
  shad[1] = p3d_LightSource[1].shadowMatrix * vertex;
  shad[2] = p3d_LightSource[2].shadowMatrix * vertex;
}
""", """
#version 330

uniform sampler2D p3d_Texture0;

uniform struct {
  vec4 ambient;
} p3d_LightModel;

uniform struct {
  vec4 ambient;
  vec4 diffuse;
  vec3 specular;
  float shininess;
} p3d_Material;

uniform struct {
  vec4 position;
  vec4 diffuse;
  vec4 specular;
  vec3 attenuation;
  vec3 spotDirection;
  float spotCosCutoff;
  float spotExponent;
  sampler2DShadow shadowMap;
  mat4 shadowMatrix;
} p3d_LightSource[3];

in vec3 vpos;
in vec3 norm;
in vec4 shad[3];

out vec4 p3d_FragColor;

void main() {
  p3d_FragColor = p3d_LightModel.ambient * p3d_Material.ambient;

  for (int i = 0; i < p3d_LightSource.length(); ++i) {
    vec3 diff = p3d_LightSource[i].position.xyz - vpos * p3d_LightSource[i].position.w;
    vec3 L = normalize(diff);
    vec3 E = normalize(-vpos);
    vec3 R = normalize(-reflect(L, norm));
    vec4 diffuse = clamp(p3d_Material.diffuse * p3d_LightSource[i].diffuse * max(dot(norm, L), 0), 0, 1);
    vec4 specular = vec4(p3d_Material.specular, 1) * p3d_LightSource[i].specular * pow(max(dot(R, E), 0), p3d_Material.shininess);

    float spotEffect = dot(normalize(p3d_LightSource[i].spotDirection), -L);

    if (spotEffect > p3d_LightSource[i].spotCosCutoff) {
      diffuse *= pow(spotEffect, p3d_LightSource[i].spotExponent);
      diffuse *= textureProj(p3d_LightSource[i].shadowMap, shad[i]);
      p3d_FragColor += diffuse / dot(p3d_LightSource[i].attenuation, vec3(1, length(diff), length(diff) * length(diff)));
    }
  }

  p3d_FragColor.a = 1;
}
""")

cm = CardMaker("card")
cm.setFrame(-5, 5, -5, 5)
card = render.attachNewNode(cm.generate())
m = Material()
m.set_diffuse((1, 1, 1, 1))
card.setMaterial(m)

red = Spotlight("red")
red.setColor((BRIGHTNESS, 0, 0, 1))
red.setExponent(EXPONENT)
red.getLens().setNearFar(5, 11)
red.getLens().setFov(30)
red_path = render.attachNewNode(red)
red_path.set_pos(1, -10, 0)
red_path.look_at(DIST * math.cos(math.pi * 1.333), 0, DIST * math.sin(math.pi * 1.3333))

green = Spotlight("green")
green.setColor((0, BRIGHTNESS, 0, 1))
green.setExponent(EXPONENT)
green.getLens().setNearFar(5, 11)
green.getLens().setFov(30)
green_path = render.attach_new_node(green)
green_path.set_pos(-1, -10, 0)
green_path.look_at(DIST * math.cos(math.pi * 0.666), 0, DIST * math.sin(math.pi * 0.6666))
green_path.set_x(green_path.get_x() + 1)

blue = Spotlight("blue")
blue.setColor((0, 0, BRIGHTNESS, 1))
blue.setExponent(EXPONENT)
blue.getLens().setNearFar(5, 11)
blue.getLens().setFov(30)
blue_path = render.attach_new_node(blue)
blue_path.set_pos(0, -10, 1)
blue_path.look_at(DIST * math.cos(0), DIST * math.sin(0), 0)
blue_path.set_y(green_path.get_y() + 1)

red.setShadowCaster(True, 4096, 4096)
green.setShadowCaster(True, 4096, 4096)
blue.setShadowCaster(True, 4096, 4096)

#red.show_frustum()
#green.show_frustum()
#blue.show_frustum()

render.set_light(red_path)
render.set_light(green_path)
render.set_light(blue_path)


sphere = loader.loadModel("models/sphere")

spheres = render.attach_new_node("spheres")
sphere.copy_to(spheres).set_pos(1.5, 0, 0)
sphere.copy_to(spheres).set_pos(0, 1.5, 0)
sphere.copy_to(spheres).set_pos(-0.75, -0.75, 1.5)
spheres.set_scale(0.5)
spheres.set_y(-1)
Sequence(
    spheres.posInterval(0.7, (0, -3, 0)),
    spheres.posInterval(0.7, (0, -1, 0))
  ).loop()

spheres.hprInterval(1, (360, 360, 360)).loop()

render.set_shader(shader)

base.trackball.node().set_pos(0, 6, 0)
base.trackball.node().set_hpr(0, -60, 30)

base.accept('a', lambda: render.set_shader_auto(True))
base.accept('s', lambda: render.set_shader(shader))
base.accept('n', lambda: render.clear_shader())
base.accept('tab', base.bufferViewer.toggleEnable)

base.run()
