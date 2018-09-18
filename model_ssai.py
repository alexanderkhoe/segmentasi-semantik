import tensorflow as tf
import numpy as np
from helpers import *

modelName = 'SSAI'

input_image = tf.placeholder(tf.float32, shape=(None, 1500, 1500, 3))
label_image = tf.placeholder(tf.float32, shape=(None, 1500, 1500, 1))

is_train = tf.placeholder_with_default(True, ())
global_step = tf.Variable(0, trainable=False)


norm_coef = 0.0005

keep_prob = tf.cond(is_train, lambda: tf.identity(0.75), lambda: tf.identity(1.0))

learning_rate = tf.train.exponential_decay(0.01, global_step, 100, 0.95, staircase=True)
tf.summary.scalar('learning_rate', learning_rate)

layer, bias = conv(input_image, "conv1", width=16, stride=4, out_depth=64)
layer = batch_norm(layer + bias, 'bn1', is_train)
layer = tf.nn.relu(layer)

layer = maxpool(layer, "pool", width=2, stride=1)

layer, bias  = conv(layer, "conv2", width=4, stride=1, out_depth=256)
layer = batch_norm(layer + bias, 'bn2', is_train)
layer = tf.nn.relu(layer)

layer = tf.nn.dropout(layer, keep_prob, name="dropout1")

layer, bias = conv(layer, "conv3", width=3, stride=1, out_depth=128)
layer = batch_norm(layer + bias, 'bn3', is_train)
layer = tf.nn.relu(layer)

layer = tf.nn.dropout(layer, keep_prob, name="dropout2")

layer, bias  = conv(layer, "conv4", width=16, stride=2, out_depth=16, transpose=True)
layer = batch_norm(layer + bias, 'bn4', is_train)
layer = tf.nn.relu(layer)

layer, bias  = conv(layer, "conv5", width=16, stride=2, out_depth=1, transpose=True)
layer = batch_norm(layer + bias, 'bn5', is_train)

result = tf.nn.sigmoid(layer)

update_ops = tf.get_collection("update_bn")

error = tf.reduce_mean(tf.nn.sigmoid_cross_entropy_with_logits(logits=layer, labels=label_image))
tf.summary.scalar('loss', error)
test_summary = tf.summary.scalar('test_loss',  tf.cond(is_train, lambda: tf.identity(0.0), lambda: tf.identity(error)))

full_error = error + norm_coef * tf.reduce_sum(tf.get_collection("l2_losses"))
tf.summary.scalar('full_error', full_error)

with tf.control_dependencies(update_ops):
    train = tf.train.MomentumOptimizer(learning_rate, 0.9).minimize(full_error, global_step=global_step)

summary = tf.summary.merge_all()