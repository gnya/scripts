/*
 * toon shader
 * author: gnya
 */

/*
 * This function retrieves the triangle's vertices and normals.
 *
 * Since `getattribute` cannnot obtain the triangle's normals,
 * it uses `trace` to fetch them by assuming that the normal N
 * near each vertex matches the vertex's actual normal.
 */
void fetch_triangle(point verts[3], vector norms[3]) {
    getattribute("geom:trianglevertices", verts);

    for (int i = 0; i < 3; i++) {
        trace(verts[i] + Ng * 1.0e-4, -Ng);
        getmessage("trace", "N", norms[i]);
    }
}

/*
 * This function calculates the displacement produced by slightly
 * deforming the triangle toward the normal ng.
 * 
 * The algorithm is based on Cycles’ implementation.
 *
 * ref: blender/intern/cycles/kernel/light/sample.h
 */
vector smooth_surface_offset(vector ng) {
    point verts[3];
    vector norms[3];

    fetch_triangle(verts, norms);

    vector uvw = vector(1.0 - u - v, u, v);
    point p = verts[0] * uvw.x + verts[1] * uvw.y + verts[2] * uvw.z;
    vector n = norms[0] * uvw.x + norms[1] * uvw.y + norms[2] * uvw.z;

    vector v01 = verts[1] - verts[0];
    vector v12 = verts[2] - verts[1];
    vector v20 = verts[0] - verts[2];

    float a = dot(norms[2] - norms[0], v20);
    float b = dot(norms[1] - norms[2], v12);
    float c = dot(norms[1] - norms[0], v01);
    float h = (a + b + c) * uvw.x * uvw.y +
        a * uvw.x * (uvw.x - 1) + b * uvw.y * (uvw.y - 1);

    if (dot(n, ng) > 0.0) {
        float h0 = max(max(dot(v01, norms[0]), dot(-v20, norms[0])), 0.0);
        float h1 = max(max(dot(-v01, norms[1]), dot(v12, norms[1])), 0.0);
        float h2 = max(max(dot(v20, norms[2]), dot(-v12, norms[2])), 0.0);

        h0 = max(dot(verts[0] - p, norms[0]) + h0, 0.0);
        h1 = max(dot(verts[1] - p, norms[1]) + h1, 0.0);
        h2 = max(dot(verts[2] - p, norms[2]) + h2, 0.0);
        h = max(min(min(h0, h1), h2), h * 0.5);
    } else {
        float h0 = max(max(dot(-v01, norms[0]), dot(v20, norms[0])), 0.0);
        float h1 = max(max(dot(v01, norms[1]), dot(-v12, norms[1])), 0.0);
        float h2 = max(max(dot(-v20, norms[2]), dot(v12, norms[2])), 0.0);

        h0 = max(dot(p - verts[0], norms[0]) + h0, 0.0);
        h1 = max(dot(p - verts[1], norms[1]) + h1, 0.0);
        h2 = max(dot(p - verts[2], norms[2]) + h2, 0.0);
        h = min(-min(min(h0, h1), h2), h * 0.5);
    }

    return n * h;
}

/*
 * This function calculates the amount by which the ray start
 * point is moved along the geometry normal.
 *
 * ref: blender/intern/cycles/kernel/light/sample.h
 */
vector ray_offset(vector L, float cutoff) {
    if (cutoff > 0.0) {
        float NL = dot(N, L);
        vector ng = (NL < 0.0 ? -Ng : Ng);
        float ngl = dot(ng, L);

        if (NL < 0.0) {
            NL = -NL;
        }
        
        float offset = 0.0;

        if (NL < cutoff) {
            offset = clamp(2.0 - (ngl + NL) / cutoff, 0.0, 1.0);
        } else {
            offset = clamp(1.0 - ngl / cutoff, 0.0, 1.0);
        }
        
        if (offset > 0.0) {
            return smooth_surface_offset(ng) * offset;
        }
    }

    return vector(0.0, 0.0, 0.0);
}
