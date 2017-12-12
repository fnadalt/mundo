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

uniform float clipo_dir;

varying vec4 vpos;

void main()
{
    vec3 clipp=vec3(0,0,1)*clipo_dir;
    vec3 pos=normalize(vec3(vpos.x, vpos.y, vpos.z-0));
    vec4 _color=vec4(0.0,0.0,abs(vpos.z),1.0);
    
    if(clipo_dir<0){
        _color=vec4(1.0,0.0,0.0,1.0);
    }
    
    //vec4 tex_color=texture2D(p3d_Texture0, gl_TexCoord[0].st);
    if(dot(clipp, pos)<0.0){
        //gl_FragColor=vec4(1,1,1,1);
        discard;
        //_color=vec4(1,0,0,1);
    }

    _color.a=1.0;
    gl_FragColor=_color;
}
