frag_src = """#version 130
#line 2
uniform sampler2D u_tex1;
uniform sampler2D u_tex2;
uniform sampler3D u_chunktex;
uniform sampler3D u_vdf_tex;

uniform float u_time;
uniform vec3 u_lightpos;
uniform vec3 u_chunksize;
uniform vec3 u_vdf_size;
uniform float u_vdf_scale;
uniform vec3 u_player_pos;
uniform vec3 u_hit_voxel;

in vec4 v_pos;
in vec3 v_normal;
in vec2 v_texcoord;

out vec4 fragColor;

float voxel_at(in vec3 pos) {
    //if (all(equal(ivec3(pos), ivec3(u_player_pos))))
    //    return 1.; 
    if (any(lessThan(pos, vec3(1))) || any(greaterThanEqual(pos, u_chunksize)))
        return 0.;
    return texelFetch(u_chunktex, ivec3(pos+.5), 0).x;
}

float distance_at(in vec3 pos) {
    pos /= u_vdf_scale;
    if (any(lessThan(pos, vec3(0))) || any(greaterThanEqual(pos, u_chunksize)))
        return 15.;
    return texture(u_vdf_tex, pos / u_chunksize).x / u_vdf_scale;
    //return texelFetch(u_vdf_tex, ivec3(mod(pos, u_vdf_size)), 0).x;
}

float voxel_density(in vec3 pos) {
    return texture(u_chunktex, (pos+vec3(0,0,.5)) / u_chunksize).y;
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
        float h = distance_at(pos) - .2;
        #if 0
            res = min( res, 10.0*h/t );
        #else
            float y = h*h/(2.0*ph);
            float d = sqrt(h*h-y*y);
            res = min(res, 10.0*d/max(0.0,t-y));
            ph = h;
        #endif
        t += d;
        if (res < 0.0001 || t >= max_dist) 
            break;
    }
    return clamp(res, 0., 1.);
}

// dilla, https://www.shadertoy.com/view/XsjXRG
float ambient_occlusion(vec3 origin, vec3 ray) {
    float delta = 0.1;
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

vec3 lighting(in vec3 lightpos, in vec3 pos, in vec3 normal, in int do_voxel) {
    vec3 lightnorm = normalize(lightpos - pos);
    float lightdist = distance(pos, lightpos);
    float d = max(0., dot(normal, lightnorm));
    d = pow(d, .5);
    if (d > 0.)
    {
        if (do_voxel==1) 
            d *= voxel_shadow_ray(pos+0.01*normal, lightnorm, lightdist);
        else
            d *= distance_field_shadow_ray(pos+0.1*normal, lightnorm, lightdist);
    }
    
    return clamp(vec3(d,d,pow(d,1.3)), .3, 1.);
}

void main() {
    vec4 tex = texture2D(u_tex1, v_texcoord);
        
    vec3 col = vec3(0);
    //col = mix(col, poscol(v_pos), .4);
    //col = mix(col, v_normal*.5+.5, .5);
    col = mix(col, tex.rgb, 1.);
    
    vec3 light = vec3(0);
    //light += lighting(u_lightpos, v_pos.xyz, v_normal);
    light += .1*vec3(0,1,1)*lighting(vec3(-20,30,40), v_pos.xyz, v_normal, 1);
    light += .7*lighting(u_player_pos + vec3(0,0,.3), v_pos.xyz, v_normal, 0);
    col *= light;
    
    //col.x += v_pos.y/10.;
    //col = mix(col, vec3(voxel_at(v_pos.xyz-v_normal*.01)), .8);
    //col = mix(col, texture2D(u_tex2, v_texcoord).xyz, .5);
    //col += texture(u_chunktex, v_pos.xyz*2.1).xyz;
    
    //col += sin(u_time+v_pos.x);
    //col = mix(col, vec3(v_texcoord, 0.), .9);
    //col = vec3(lightdot);  
    
    //col *= vec3(1. - voxel_density(v_pos.xyz));
    
    //col += distance_at(vec3(v_pos.xy, u_time))/3.;
    
    //col *= .8+.4*ambient_occlusion(v_pos.xyz, v_normal);
    
    if (ivec2(u_hit_voxel) == ivec2(v_pos))
        col *= 2.;
    
    fragColor = vec4(col, 1);
}
"""
