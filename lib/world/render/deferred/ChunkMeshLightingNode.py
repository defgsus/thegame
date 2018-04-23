import glm

from lib.opengl import *
from lib.opengl.core.base import *
from lib.opengl.postproc.base import PostProcNode


frag_src = """
#line 9
uniform sampler2D u_color_tex;
uniform sampler2D u_normal_tex;
uniform sampler2D u_position_tex;
uniform sampler3D u_vdf_tex;

uniform vec4 u_lightpos; // pos, amt
uniform vec3 u_chunksize;
uniform vec3 u_vdf_size;
uniform float u_vdf_scale;
uniform vec3 u_player_pos;
uniform vec3 u_hit_voxel;
uniform int u_debug_view;

float distance_at(in vec3 pos) {
    pos /= u_vdf_scale;
    if (any(lessThan(pos, vec3(0))) || any(greaterThanEqual(pos, u_chunksize)))
        return 15.;
    return texture(u_vdf_tex, pos / u_chunksize).x / u_vdf_scale;
    //return texelFetch(u_vdf_tex, ivec3(mod(pos, u_vdf_size)), 0).x;
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
        if (h < 0.05) { res = 0.; break; }
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

vec3 lighting(in vec3 lightpos, in vec3 pos, in vec3 normal, in float spec_amt) {
    vec3 lightnorm = normalize(lightpos - pos);
    float lightdist = distance(pos, lightpos);
    float d = max(0., dot(normal, lightnorm));
    
    if (d > 0.)
    {
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

void mainImage(out vec4 fragColor, in vec2 fragCoord, in vec2 texCoord) {
    
    vec4 tex = texture(u_color_tex, texCoord);
    vec3 normal = texture(u_normal_tex, texCoord).xyz;
    vec3 position = texture(u_position_tex, texCoord).xyz;
    
    float spec_amt = texture(u_normal_tex, texCoord).w;
        
    vec3 col = tex.xyz;
    
    if (u_debug_view == 0) 
    {    
        vec3 light = vec3(0);
        light += u_lightpos.w * lighting(u_lightpos.xyz, position, normal, spec_amt);
        // moonlight
        //light += .5*vec3(0,1,1)*lighting(vec3(-20,30,40), position, normal, spec_amt);
        // player light
        light += vec3(1,.6,.3)*lighting(u_player_pos + vec3(0,0,.9), position, normal, spec_amt);
        col *= light;
        
        col += .09*environment_color(normal);
        
        // hit highlight
        vec3 hitbox = abs(u_hit_voxel + .5 - position);
        float hit = clamp(1.4-dot(hitbox, hitbox), 0., 1.);
        col = (col * (1.+pow(hit, 2.))) + .3*u_lightpos.w*pow(hit, 3.);
        
        //col = mix(vec3(1), col, tex.w);
    }
    
    if (u_debug_view == 1) 
    {
        col = vec3(.5);
        
        col += .6*environment_color(normal);
        
        //col *= vec3(distance_at(position));
    }
    
    if (u_debug_view == 2) 
    {
        //col = vec3(distance_at(position));
        
        col = .5+.4*normal;
        
        //col *= v_ambient;
    }
    
    if (u_debug_view == 3) 
    {
        col = .7+.3*sin(position*5.);
    }
    
    if (u_debug_view == 4) 
    {
        vec3 ln = normalize(u_lightpos.xyz - position);
        float d = .5+.5*dot(normal, ln);
        col = vec3(d);
    }
    
    fragColor = vec4(col, 1);
}
"""


class ChunkMeshLightingNode(PostProcNode):

    def __init__(self, world, renderer, name):
        super().__init__(name)
        self.world = world
        self.renderer = renderer
        self.vdf_tex = None
        self.vdf_scale = 1

    @property
    def chunk(self):
        return self.world.chunk

    def get_code(self):
        return frag_src

    def create(self, render_settings):
        # voxel distance field
        if self.vdf_tex is None:
            self.vdf_tex = self.chunk.create_voxel_distance_texture3d(scale=self.vdf_scale)

    def update_uniforms(self, shader, rs, pass_num):

        proj = rs.projection.matrix

        lightpos = glm.vec3(self.world.click_voxel) + (.5,.5,1.5)
        shader.set_uniform("u_projection", proj)
        shader.set_uniform("u_time", rs.time)
        shader.set_uniform("u_lightpos", glm.vec4(lightpos, 1))
        shader.set_uniform("u_color_tex", 0)
        shader.set_uniform("u_normal_tex", 1)
        shader.set_uniform("u_position_tex", 2)
        shader.set_uniform("u_vdf_tex", 3)
        shader.set_uniform("u_chunksize", self.chunk.size())
        shader.set_uniform("u_vdf_size", self.vdf_tex.size())
        shader.set_uniform("u_vdf_scale", self.vdf_scale)
        shader.set_uniform("u_player_pos", self.world.agents["player"].sposition)
        shader.set_uniform("u_hit_voxel", self.world.click_voxel)
        shader.set_uniform("u_debug_view", self.world.debug_view)

        Texture2D.set_active_texture(3)
        self.vdf_tex.bind()
        Texture2D.set_active_texture(0)
