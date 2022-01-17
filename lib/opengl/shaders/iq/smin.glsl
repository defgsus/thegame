/**
 from IQ, https://iquilezles.org/www/articles/smin/smin.htm
*/

// exponential smooth min (k=32)
float smin_exp( float a, float b, float k )
{
    float res = exp2( -k*a ) + exp2( -k*b );
    return -log2( res )/k;
}

// power smooth min (k=8)
float smin_pow( float a, float b, float k )
{
    a = pow( a, k ); b = pow( b, k );
    return pow( (a*b)/(a+b), 1.0/k );
}

// root smooth min (k=0.01)
float smin_sqrt( float a, float b, float k )
{
    float h = a-b;
    return 0.5*( (a+b) - sqrt(h*h+k) );
}

// polynomial smooth min 1 (k=0.1)
float smin_poly( float a, float b, float k )
{
    float h = clamp( 0.5+0.5*(b-a)/k, 0.0, 1.0 );
    return mix( b, a, h ) - k*h*(1.0-h);
}

// polynomial smooth min 2 (k=0.1)
float smin_poly2( float a, float b, float k )
{
    float h = max( k-abs(a-b), 0.0 )/k;
    return min( a, b ) - h*h*k*(1.0/4.0);
}
