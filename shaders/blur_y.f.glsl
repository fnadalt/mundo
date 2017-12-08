#version 120

uniform sampler2D p3d_Texture0;

void main()
{
    vec3 offset=vec3(1.0/1024.0, 5.0/1024.0, 9.0/1024.0);
    vec4 color=texture2D(p3d_Texture0, vec2(gl_TexCoord[0].s, gl_TexCoord[0].t-offset.x)) * 5.0;
    color+=texture2D(p3d_Texture0, vec2(gl_TexCoord[0].s, gl_TexCoord[0].t-offset.y)) * 8.0;
    color+=texture2D(p3d_Texture0, vec2(gl_TexCoord[0].s, gl_TexCoord[0].t-offset.z)) * 10.0;
    color+=texture2D(p3d_Texture0, vec2(gl_TexCoord[0].s, gl_TexCoord[0].t+offset.x)) * 10.0;
    color+=texture2D(p3d_Texture0, vec2(gl_TexCoord[0].s, gl_TexCoord[0].t+offset.y)) * 8.0;
    color+=texture2D(p3d_Texture0, vec2(gl_TexCoord[0].s, gl_TexCoord[0].t+offset.z)) * 5.0;
    color*=0.030;
    gl_FragColor=color;
}
