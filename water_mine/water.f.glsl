#version 130

uniform sampler2D p3d_Texture0;

in vec4 vpos;

void main()
{
    vec2 xy_pos=vpos.xy;
    vec2 ndc= (xy_pos/vpos.w)/2.0+0.5;
    vec2 tc=vec2(ndc.x,ndc.y);
    gl_FragColor=texture2D(p3d_Texture0, tc);
    //gl_FragColor.a=0.7;
}
