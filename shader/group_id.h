/*
 * toon shader (0.4.1)
 * author: gnya
 */

#define GET_SHADOW(id) mod(id, 100)
#define GET_TRANSPARENT(id) trunc(id / 100)
#define GET_SHADOW_PROPS(id) trunc(id / 10000)

/*
 * Get this shadow group id and shadow props.
 */
void get_this_shadow_group(output float group, output float props) {
    float obj_id, mat_id;
    getattribute("object:index", obj_id);
    getattribute("material:index", mat_id);

    group = GET_SHADOW(obj_id) ? GET_SHADOW(obj_id) : GET_SHADOW(mat_id);
    props = GET_SHADOW_PROPS(obj_id) ? GET_SHADOW_PROPS(obj_id) : GET_SHADOW_PROPS(mat_id);
}

/*
 * Get hit shadow group id and shadow props.
 */
void get_hit_shadow_group(output float group, output float props) {
    float obj_id, mat_id;
    getmessage("trace", "object:index", obj_id);
    getmessage("trace", "material:index", mat_id);

    group = GET_SHADOW(obj_id) ? GET_SHADOW(obj_id) : GET_SHADOW(mat_id);
    props = GET_SHADOW_PROPS(obj_id) ? GET_SHADOW_PROPS(obj_id) : GET_SHADOW_PROPS(mat_id);
}

/*
 * Get this transparent group id.
 */
void get_this_transparent_group(output float group) {
    float obj_id, mat_id;
    getattribute("object:index", obj_id);
    getattribute("material:index", mat_id);

    group = GET_TRANSPARENT(obj_id) ? GET_TRANSPARENT(obj_id) : GET_TRANSPARENT(mat_id);
}

/*
 * Get hit transparent group id.
 */
void get_hit_transparent_group(output float group) {
    float obj_id, mat_id;
    getmessage("trace", "object:index", obj_id);
    getmessage("trace", "material:index", mat_id);

    group = GET_TRANSPARENT(obj_id) ? GET_TRANSPARENT(obj_id) : GET_TRANSPARENT(mat_id);
}
