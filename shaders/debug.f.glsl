
#version 120

//uniform sampler2D p3d_Texture0;

uniform struct {
    vec4 ambient;
} p3d_LightModel;

uniform struct {
    vec4 ambient;
    vec4 diffuse;
    vec4 emission;
    vec3 specular;
    float shininess;
} p3d_Material;

uniform struct {
    vec4 color;
    vec4 ambient;
    vec4 diffuse;
    vec4 specular;
    vec4 position;
    vec3 spotDirection;
    float spotExponent;
    float spotCutoff;
    float spotCosCutoff;
    vec3 attenuation;
    //sampler2DShadow shadowMap;
    //mat4 shadowViewMatrix;
} p3d_LightSource[8];

uniform vec4 p3d_ClipPlane[1];
//uniform float dummy_input;

varying vec4 vpos;
varying vec4 vpos_inv;
varying vec4 clipo;

void main()
{
    vec4 _color=vec4(0.0,0.0,abs(vpos.z),1.0);

    /*if(dummy_input<0.0){
        _color=vec4(1.0,0.0,0.0,1.0);
    }*/
    
    if(p3d_ClipPlane[0].z!=0.0){
        //_color=vec4(1.0,0.0,0.0,1.0);
    }
    
    //vec4 tex_color=texture2D(p3d_Texture0, gl_TexCoord[0].st);
    if(dot(p3d_ClipPlane[0],vpos_inv)<0.0){
        //gl_FragColor=vec4(1,1,1,1);
        //discard;
        //_color=vec4(0,1,0,1);
    }

    _color.a=1.0;
    gl_FragColor=_color;
}
