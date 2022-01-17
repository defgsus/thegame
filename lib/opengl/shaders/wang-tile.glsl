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

float wang_tile_distance(in vec2 uv, in int idx) {
    float d = 1e6;
    if ((idx & 255) == 255)
        d = -1.;
    else {
        float radius = .5;
        if (bool(idx & T)) {
            d = smin(d, sdBox(uv - vec2(0, 1), vec2(1, radius)));
        }
        if (bool(idx & B)) {
            d = smin(d, sdBox(uv - vec2(0, -1), vec2(1, radius)));
        }
        if (bool(idx & L)) {
            d = smin(d, sdBox(uv - vec2(-1, 0), vec2(radius, 1)));
        }
        if (bool(idx & R)) {
            d = smin(d, sdBox(uv - vec2(1, 0), vec2(radius, 1)));
        }

        if (bool(idx & T)) {
            if (bool(idx & L))
                d = smin(d, sdCircle(uv - vec2(-.25, .25), radius));
            if (bool(idx & R))
                d = smin(d, sdCircle(uv - vec2(.25, .25), radius));
        }
        if (bool(idx & B)) {
            if (bool(idx & L))
                d = smin(d, sdCircle(uv - vec2(-.25, -.25), radius));
            if (bool(idx & R))
                d = smin(d, sdCircle(uv - vec2(.25, -.25), radius));
        }

        if (bool(idx & TL)) {
            d = smin(d, sdCircle(uv - vec2(-1, 1), radius));
        }
        if (bool(idx & TR)) {
            d = smin(d, sdCircle(uv - vec2(1, 1), radius));
        }
        if (bool(idx & BL)) {
            d = smin(d, sdCircle(uv - vec2(-1, -1), radius));
        }
        if (bool(idx & BR)) {
            d = smin(d, sdCircle(uv - vec2(1, -1), radius));
        }
    }
    return d;
}


/*
vec3 wang_tile(in vec2 uv, in int idx) {
    float d = 1e6;
    if ((idx & 255) == 255)
        d = -1.;
    else {
        float radius = .5;
        if (bool(idx & T)) {
            d = smin(d, sdBox(uv - vec2(0, 1), vec2(1, radius)));
            d = smin(d, sdCircle(uv - vec2(-1, 1), radius));
            d = smin(d, sdCircle(uv - vec2(1, 1), radius));
        }
        if (bool(idx & B)) {
            d = smin(d, sdBox(uv - vec2(0, -1), vec2(1, radius)));
            d = smin(d, sdCircle(uv - vec2(-1, -1), radius));
            d = smin(d, sdCircle(uv - vec2(1, -1), radius));
        }
        if (bool(idx & L)) {
            d = smin(d, sdBox(uv - vec2(-1, 0), vec2(radius, 1)));
            d = smin(d, sdCircle(uv - vec2(-1, 1), radius));
            d = smin(d, sdCircle(uv - vec2(-1, -1), radius));
        }
        if (bool(idx & R)) {
            d = smin(d, sdBox(uv - vec2(1, 0), vec2(radius, 1)));
            d = smin(d, sdCircle(uv - vec2(1, 1), radius));
            d = smin(d, sdCircle(uv - vec2(1, -1), radius));
        }

        if (bool(idx & T)) {
            if (bool(idx & L))
                d = smin(d, sdCircle(uv - vec2(-.25, .25), radius));
        }

        if (bool(idx & TL)) {
            d = smin(d, sdCircle(uv - vec2(-1, 1), radius));
            d = smin(d, sdBox(uv - vec2(-1, 2), vec2(radius, 1)));
        }
        if (bool(idx & TR)) {
            d = smin(d, sdCircle(uv - vec2(1, 1), radius));
            d = smin(d, sdBox(uv - vec2(1, 2), vec2(radius, 1)));
            d = smin(d, sdBox(uv - vec2(2, 1), vec2(1, radius)));
        }
        if (bool(idx & BL)) {
            d = smin(d, sdCircle(uv - vec2(-1, -1), radius));
            d = smin(d, sdBox(uv - vec2(-1, -2), vec2(radius, 1)));
        }
        if (bool(idx & BR)) {
            d = smin(d, sdCircle(uv - vec2(1, -1), radius));
            d = smin(d, sdBox(uv - vec2(1, -2), vec2(radius, 1)));
        }
    }
    vec3 col = vec3(
        .3 + .7 * smoothstep(0.03, -0.03, d)
    );
    return col;
}
*/