#version 120

uniform sampler2D iChannel0;
uniform vec2 iResolution;

uniform float warp; // Screen curvature from 0.0
uniform float scan; // Screen scan effect (Lines) from 0.0

void mainImage(out vec4 fragColor, in vec2 fragCoord)
{
    // Create a normalized uv map
    vec2 uv = fragCoord / iResolution.xy;
    vec2 dc = abs(0.5 - uv);
    dc *= dc;

    // warp the image
    uv.x -= 0.5;
    uv.x *= 1.0 + (dc.y * (0.3 * warp));
    uv.x += 0.5;

    uv.y -= 0.5;
    uv.y *= 1.0 + (dc.x * (0.4 * warp));
    uv.y += 0.5;

    // Make the outside black
    if (uv.x < 0.0 || uv.x > 1.0 || uv.y < 0.0 || uv.y > 1.0) {
        fragColor = vec4(0.0, 0.0, 0.0, 1.0);
    } else {
        // Intensity of scanlines
        float apply = abs(sin(uv.y * iResolution.y * 3.1415) * 0.5 * scan);
        vec3 color = texture2D(iChannel0, uv).rgb;
        fragColor = vec4(mix(color, vec3(0.0), apply), 1.0);
    }
}

void main() {
    vec4 color;
    mainImage(color, gl_FragCoord.xy);
    gl_FragColor = color;
}