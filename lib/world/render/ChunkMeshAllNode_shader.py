vert_src = """
#version 150
#line 3
uniform mat4 u_projection;

in vec4 a_position;
in vec3 a_normal;
in vec4 a_color;
in vec2 a_texcoord;
in vec3 a_ambient;

out vec4 v_pos;
out vec3 v_normal;
out vec4 v_color;
out vec2 v_texcoord;
out vec3 v_ambient;
out mat3 v_normal_space;

/** Returns the matrix to multiply the light-direction normal */
mat3 calc_light_matrix(mat4 transform)
{
    // normal in world coordinates
    vec3 norm = transpose(inverse(mat3(transform))) * a_normal;

    vec3 tangent =  vec3(-norm.z, -norm.y,  norm.x);
    vec3 binormal = vec3(-norm.x,  norm.z, -norm.y);
    return mat3(tangent, -binormal, norm);
}

void main()
{
    v_pos = a_position;
    v_normal = a_normal;
    v_color = a_color;
    v_texcoord = a_texcoord;
    v_ambient = a_ambient;
    v_normal_space = calc_light_matrix(mat4(1));
    gl_Position = u_projection * a_position;
}

"""


frag_src = """
#version 130
#line 46
uniform sampler2D u_tex1;
uniform sampler3D u_chunk_tex;
uniform sampler3D u_vdf_tex;

uniform float u_time;
uniform vec4 u_lightpos; // pos, amt
uniform vec3 u_chunksize;
uniform vec3 u_vdf_size;
uniform float u_vdf_scale;
uniform vec3 u_player_pos;
uniform vec3 u_hit_voxel;
uniform int u_debug_view;

in vec4 v_pos;
in vec3 v_normal;
in vec2 v_texcoord;
in vec3 v_ambient;
in mat3 v_normal_space;

out vec4 fragColor;

float voxel_at(in vec3 pos) {
    //if (all(equal(ivec3(pos), ivec3(u_player_pos))))
    //    return 1.; 
    if (any(lessThan(pos, vec3(1))) || any(greaterThanEqual(pos, u_chunksize)))
        return 0.;
    return texelFetch(u_chunk_tex, ivec3(pos+.5), 0).x;
}

float distance_at(in vec3 pos) {
    pos /= u_vdf_scale;
    if (any(lessThan(pos, vec3(0))) || any(greaterThanEqual(pos, u_chunksize)))
        return 15.;
    return texture(u_vdf_tex, pos / u_chunksize).x / u_vdf_scale;
    //return texelFetch(u_vdf_tex, ivec3(mod(pos, u_vdf_size)), 0).x;
}

float voxel_density(in vec3 pos) {
    return texture(u_chunk_tex, (pos+vec3(0,0,.5)) / u_chunksize).y;
}

// Inigo Quilez, Reinder Nijhoff, https://www.shadertoy.com/view/4ds3WS
float voxel_shadow_ray(in vec3 ro, in vec3 rd, in float max_dist) 
{
    vec3 pos = floor(ro);
    vec3 ri = 1.0/rd;
    vec3 rs = sign(rd);
    vec3 dis = (pos-ro + 0.5 + rs*0.5) * ri;

    float res = 1.0;

    for(int i=0; i<15; i++) 
    {
        if (any(lessThan(pos, vec3(0))) || any(greaterThanEqual(pos, u_chunksize))) { break; }
        if (distance(ro, pos) >= max_dist) { break; }
        
        if (voxel_at(pos) > 0.) { res *= 0.0; break; }
        
        //res -= voxel_density(pos+vec3(0,0,1))*.1;
        
        vec3 mm = step(dis.xyz, dis.yxy) * step(dis.xyz, dis.zzx);
        dis += mm * rs * ri;
        pos += mm * rs;
    }

    return res;
}

vec2 distance_field_ray(in vec3 ro, in vec3 rd, in float max_dist) 
{
    float t = 0.;
    for (int i=0; i<30; ++i) 
    {
        float d = distance_at(ro + t * rd);
        if (d <= .1) 
            return vec2(t, 1.);
        if (t >= max_dist)
            return vec2(t, 0.);
        t += d;
    }
    return vec2(t, 0.);
}

// Sebastian Aaltonen, iq, https://www.shadertoy.com/view/lsKcDD
float distance_field_shadow_ray(in vec3 ro, in vec3 rd, in float max_dist) 
{
    float t = 0.1;
    float res = 1.;
    float ph = 1e10;
    for (int i=0; i<30; ++i) 
    {
        vec3 pos = ro + t * rd;
        if (any(lessThan(pos, vec3(0))) || any(greaterThanEqual(pos, u_chunksize-1.)))
            break;
        float h = distance_at(pos) - .3;
        #if 0
            res = min( res, 10.0*h/t );
        #else
            float y = h*h/(2.0*ph);
            float d = sqrt(h*h-y*y);
            res = min(res, 10.0*d/max(0.0,t-y));
            ph = h;
        #endif
        t += max(0.1, h);
        if (res < 0.0001 || t >= max_dist) 
            break;
    }
    return clamp(res, 0., 1.);
}

// dilla, https://www.shadertoy.com/view/XsjXRG
float ambient_occlusion(vec3 origin, vec3 ray) {
    float delta = 0.01;
    const int samples = 6;
    float r = 0.0;
    for (int i = 1; i <= samples; ++i) {
        float t = delta * float(i);
        vec3 pos = origin + ray * t;
        float dist = distance_at(pos);
        float len = abs(t - dist);
        r += len * pow(2.0, -float(i));
    }
    return r;
}

vec3 lighting(in vec3 lightpos, in vec3 pos, in vec3 normal, in int do_voxel, in float spec_amt) {
    vec3 lightnorm = normalize(lightpos - pos);
    float lightdist = distance(pos, lightpos);
    float d = max(0., dot(normal, lightnorm));
    
    if (d > 0.)
    {
        if (do_voxel==1) 
            d *= voxel_shadow_ray(pos+0.01*normal, lightnorm, lightdist);
        else
            d *= distance_field_shadow_ray(pos+0.1*normal, lightnorm, lightdist);
    }
    
    float phong = .1 + .9 * d;
    float spec = pow(d, 2. + spec_amt * 3.);
    
    d = phong + spec * spec_amt * 50.;
    
    return clamp(vec3(d,d,d), 0., 1.);
}

vec3 environment_color(in vec3 dir) {
    float h = dir.z;
    
    vec3 high_sky = vec3(.1, .4, .7);
    vec3 low_sky = vec3(.5, .3, .9);
    vec3 sub = vec3(0);
    
    vec3 col = mix(low_sky, high_sky, clamp(h*5., 0., 1.));
    col = mix(col, sub, clamp(-h*5., 0., 1.));
    
    return col;
}

void main() {
    vec4 tex = texture2D(u_tex1, v_texcoord);
        
    vec3 col = vec3(0);
    
    vec3 normal = vec3(0, 0, 1);        
    vec2 v_normcoord = v_texcoord + vec2(.5, 0.);
    vec4 normal_texel = texture2D(u_tex1, v_normcoord);
    normal = normalize(mix(normal, normal_texel.xyz, normal_texel.w));
    normal = v_normal_space * normal;
    
    if (u_debug_view == 0) 
    {    
        //col = mix(col, poscol(v_pos), .4);
        //col = mix(col, normal*.5+.5, .5);
        col = mix(col, tex.rgb, 1.);
        
        // ambient occlusion #1
        col *= pow(distance_at(v_pos.xyz), .5);
        // ambient occlusion #2
        col *= v_ambient;
        
        vec3 light = vec3(0);
        float spec_amt = normal_texel.w;
        light += u_lightpos.w * lighting(u_lightpos.xyz, v_pos.xyz, normal, 0, spec_amt);
        // moonlight
        //light += .5*vec3(0,1,1)*lighting(vec3(-20,30,40), v_pos.xyz, normal, 1, spec_amt);
        // player light
        light += vec3(1,.6,.3)*lighting(u_player_pos + vec3(0,0,.9), v_pos.xyz, normal, 0, spec_amt);
        col *= light;
        
        col += .09*environment_color(normal);
        
        //col.x += v_pos.y/10.;
        //col = mix(col, vec3(voxel_at(v_pos.xyz-normal*.01)), .8);
        //col = mix(col, texture2D(u_tex1, v_pos.xy).xyz, .5);
        //col += texture(u_chunk_tex, v_pos.xyz*2.1).xyz;
        
        //col += sin(u_time+v_pos.x);
        //col = mix(col, vec3(v_texcoord, 0.), .9);
        //col = vec3(lightdot);  
        
        //col *= vec3(1. - voxel_density(v_pos.xyz));
        
        //col += distance_at(vec3(v_pos.xy, u_time))/3.;
        
        //col *= .5+.5*ambient_occlusion(v_pos.xyz, normal);
        
        // hit highlight
        vec3 hitbox = abs(u_hit_voxel + .5 - v_pos.xyz);
        float hit = clamp(1.4-dot(hitbox, hitbox), 0., 1.);
        col = (col * (1.+pow(hit, 2.))) + .3*u_lightpos.w*pow(hit, 3.);
        
        col = mix(vec3(1), col, tex.w);
    }
    
    if (u_debug_view == 1) 
    {
        col = vec3(.6);
        
        col += .2*environment_color(normal);
        
        col *= v_ambient;
    }
    
    if (u_debug_view == 2) 
    {
        col = vec3(distance_at(v_pos.xyz));
        
        col += .4*normal;
        
        col *= v_ambient;
    }
    
    fragColor = vec4(col, tex.w);
}
"""
