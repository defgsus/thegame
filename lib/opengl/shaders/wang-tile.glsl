#include <iq/smin.glsl>
#include <iq/sdf.glsl>
#line 2

#define T 1
#define R 2
#define B 4
#define L 8
#define TL 16
#define TR 32
#define BL 64
#define BR 128

float smin(in float a, in float b) {
    return smin_exp(a, b, 4.);
}

vec3 wang_tile(in vec2 uv, in int idx) {
    float d = 1e6;
    if ((idx & 255) == 255)
        d = -1.;
    else {
        float radius = .5;
        if (bool(idx & T))
            d = smin(d, sdBox(uv - vec2(0, 1), vec2(1, radius)));
        if (bool(idx & B))
            d = smin(d, sdBox(uv - vec2(0, -1), vec2(1, radius)));
        if (bool(idx & L))
            d = smin(d, sdBox(uv - vec2(-1, 0), vec2(radius, 1)));
        if (bool(idx & R))
            d = smin(d, sdBox(uv - vec2(1, 0), vec2(radius, 1)));

        if (bool(idx & TL))
            d = smin(d, sdCircle(uv - vec2(-1, 1), radius));
        if (bool(idx & TR))
            d = smin(d, sdCircle(uv - vec2(1, 1), radius));
        if (bool(idx & BL))
            d = smin(d, sdCircle(uv - vec2(-1, -1), radius));
        if (bool(idx & BR))
            d = smin(d, sdCircle(uv - vec2(1, -1), radius));
    }
    vec3 col = vec3(
        .3 + .7 * smoothstep(0.03, -0.03, d)
    );
    return col;
}


/*
vec3 wang_tile(in vec2 uv, in int idx) {
    float d = 1e6;
    if ((idx & 255) == 255)
        d = 0.;
    else {
        if (bool(idx & (TL | T | TR))) {
            float start = 1., end = -1.;
            if (bool(idx & TL))
                start = -1.;
            if (bool(idx & T))
                start = min(start, 0.), end = max(end, 0.);
            if (bool(idx & TR))
                end = 1;

            d = min(d, length(uv - vec2(start, 1)) - .5);
        }

        if (bool(idx & B))
            d = min(d, length(uv - vec2(0, -1)) - .2);
        if (bool(idx & L))
            d = min(d, length(uv - vec2(-1, 0)) - .2);
        if (bool(idx & R))
            d = min(d, length(uv - vec2(1, 0)) - .2);

        if (bool(idx & TL))
            d = min(d, length(uv - vec2(-1, 1)) - .2);

    }
    vec3 col = vec3(
        .3 + .7 * smoothstep(0.01, -0.01, d)
    );
    return col;
}
*/