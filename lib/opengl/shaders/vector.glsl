

vec2 rotate_z(in vec2 v, in float radians) {
    float sa = sin(radians), ca = cos(radians);
    return vec2(
        v.x * ca - v.y * sa,
        v.x * sa + v.y * ca
    );
}