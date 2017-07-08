// simple vertex shader

void main()
{
	gl_Position    = gl_ModelViewProjectionMatrix * gl_Vertex;
	gl_FrontColor  = gl_Color;
    //
    mat4 scaleMatrix( 0.5f, 0.0f, 0.0f, 0.5f,
                                0.0f, 0.5f, 0.0f, 0.5f,
                                0.0f, 0.0f, 0.5f, 0.5f,
                                0.0f, 0.0f, 0.0f, 1.0f );
    //
	gl_TexCoord[0] = gl_MultiTexCoord0;
}
